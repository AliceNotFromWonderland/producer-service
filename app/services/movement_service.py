"""
Немного о бизнес-логике выдачи/списания + резервации остатков:

- "Доступный остаток" для `issue`/`write-off` = физический остаток
  (`stock_balance.quantity`) **минус** всё, что сейчас держат *активные*
  резервации на этом материале/локации — по умолчанию зарезервированное
  никому не доступно.
- Исключение — `issue`: если у сотрудника, на которого оформляется выдача,
  есть собственная активная резервация на этот материал/локацию, её
  количество прибавляется обратно перед сравнением с запрошенным
  количеством — то есть сотрудник всегда может забрать то, что
  зарезервировано именно под него, даже если для всех остальных этот объём
  недоступен.
- Как только `issue` полностью покрывает резервацию по количеству, её
  `status` меняется на `fulfilled`. Если выдача меньше зарезервированного —
  резервация остаётся `active`: в таблице `reservation` (по исходной схеме)
  нет отдельного поля "уже выдано/остаток резервации", поэтому частичное
  погашение через несколько выдач подряд не отслеживается (это надо было бы усложнять 
  логику бд, а мне лень, поэтому правила будут такие, хз логично ли или нет).
- Поле `employee_id` в `reservation` теперь поэтому стало обязательным :)

"""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import ConflictError, NotFoundError, UnprocessableError
from app.models import (
    Employee,
    Location,
    Material,
    MaterialMovement,
    MovementType,
    Reservation,
    StockBalance,
    Warehouse,
)
from app.schemas import (
    EmployeeBrief,
    LocationBrief,
    MaterialBrief,
    MovementCreate,
    MovementOut,
    WarehouseBrief,
)
from app.services import outbox_service

CODE_INCOME = "INCOME"
CODE_ISSUE = "ISSUE"
CODE_WRITE_OFF = "WRITE_OFF"

_MOVEMENT_LOAD_OPTIONS = (
    selectinload(MaterialMovement.material),
    selectinload(MaterialMovement.warehouse),
    selectinload(MaterialMovement.location),
    selectinload(MaterialMovement.movement_type),
    selectinload(MaterialMovement.employee),
)


async def _load_related(db: AsyncSession, payload: MovementCreate):
    material = await db.get(Material, payload.material_id)
    if material is None:
        raise NotFoundError(f"Material {payload.material_id} not found")

    warehouse = await db.get(Warehouse, payload.warehouse_id)
    if warehouse is None:
        raise NotFoundError(f"Warehouse {payload.warehouse_id} not found")

    location = await db.get(Location, payload.location_id)
    if location is None:
        raise NotFoundError(f"Location {payload.location_id} not found")

    employee = await db.get(Employee, payload.employee_id)
    if employee is None:
        raise NotFoundError(f"Employee {payload.employee_id} not found")

    return material, warehouse, location, employee


def _validate_business_rules(payload: MovementCreate, location: Location, warehouse: Warehouse) -> None:
    if payload.quantity <= 0:
        raise UnprocessableError("quantity must be greater than 0")
    if location.warehouse_id != warehouse.id:
        raise UnprocessableError("location_id does not belong to the specified warehouse_id")


async def _get_movement_type(db: AsyncSession, code: str) -> MovementType:
    stmt = select(MovementType).where(MovementType.code == code)
    movement_type = (await db.execute(stmt)).scalar_one_or_none()
    if movement_type is None:
        raise RuntimeError(
            f"Movement type '{code}' is not configured."
        )
    return movement_type


async def _get_or_create_balance(db: AsyncSession, material_id: int, location_id: int) -> StockBalance:
    balance = await db.get(
        StockBalance,
        {"material_id": material_id, "location_id": location_id},
        with_for_update=True,
    )
    if balance is None:
        balance = StockBalance(material_id=material_id, location_id=location_id, quantity=0)
        db.add(balance)
        await db.flush()
    return balance    


async def _get_active_reserved_quantity(db: AsyncSession, material_id: int, location_id: int) -> float:
    """Sum of all *active* reservations for this material at this location."""
    stmt = select(func.coalesce(func.sum(Reservation.quantity), 0)).where(
        Reservation.material_id == material_id,
        Reservation.location_id == location_id,
        Reservation.status == "active",
    )
    return float((await db.execute(stmt)).scalar_one())


async def _get_own_active_reservation(
    db: AsyncSession, material_id: int, location_id: int, employee_id: int
) -> Reservation | None:
    """The requesting employee's own active reservation, if any (oldest first)."""
    stmt = (
        select(Reservation)
        .where(
            Reservation.material_id == material_id,
            Reservation.location_id == location_id,
            Reservation.employee_id == employee_id,
            Reservation.status == "active",
        )
        .order_by(Reservation.created_at.asc())
    )
    return (await db.execute(stmt)).scalars().first()


async def create_income(db: AsyncSession, payload: MovementCreate) -> MaterialMovement:
    material, warehouse, location, employee = await _load_related(db, payload)
    _validate_business_rules(payload, location, warehouse)

    movement_type = await _get_movement_type(db, CODE_INCOME)
    balance = await _get_or_create_balance(db, material.id, location.id)
    balance.quantity = float(balance.quantity) + payload.quantity
    balance.last_updated = datetime.now(timezone.utc)

    return await _persist_movement(db, payload, material, warehouse, location, employee, movement_type)

# общая логика для выдачи и списания
async def _create_outgoing(db: AsyncSession, payload: MovementCreate, code: str) -> MaterialMovement:
    material, warehouse, location, employee = await _load_related(db, payload)
    _validate_business_rules(payload, location, warehouse)

    movement_type = await _get_movement_type(db, code)

    balance = await db.get(
        StockBalance,
        {"material_id": material.id, "location_id": location.id},
        with_for_update=True,
    )
    physical = float(balance.quantity) if balance else 0.0

    reserved_qty = await _get_active_reserved_quantity(db, material.id, location.id)

    own_reservation: Reservation | None = None
    if code == CODE_ISSUE:
        own_reservation = await _get_own_active_reservation(db, material.id, location.id, employee.id)
    own_reserved_amount = float(own_reservation.quantity) if own_reservation else 0.0

    available = physical - reserved_qty + own_reserved_amount
    if payload.quantity > available:
        raise ConflictError({"error": "insufficient stock", "available_quantity": available})

    balance.quantity = physical - payload.quantity
    balance.last_updated = datetime.now(timezone.utc)

    if own_reservation is not None and payload.quantity >= float(own_reservation.quantity):
        own_reservation.status = "fulfilled"

    return await _persist_movement(db, payload, material, warehouse, location, employee, movement_type)


async def create_issue(db: AsyncSession, payload: MovementCreate) -> MaterialMovement:
    return await _create_outgoing(db, payload, CODE_ISSUE)


async def create_write_off(db: AsyncSession, payload: MovementCreate) -> MaterialMovement:
    return await _create_outgoing(db, payload, CODE_WRITE_OFF)


async def _persist_movement(
    db: AsyncSession,
    payload: MovementCreate,
    material: Material,
    warehouse: Warehouse,
    location: Location,
    employee: Employee,
    movement_type: MovementType,
) -> MaterialMovement:
    movement = MaterialMovement(
        material_id=material.id,
        warehouse_id=warehouse.id,
        location_id=location.id,
        movement_type_id=movement_type.id,
        quantity=payload.quantity,
        employee_id=employee.id,
        unit_price=payload.unit_price,
        comment=payload.comment,
        document_ref=payload.document_ref,
    )
    # Attaches the already-loaded related objects directly so the response
    # can be built right after commit without extra SELECTs.
    movement.material = material
    movement.warehouse = warehouse
    movement.location = location
    movement.employee = employee
    movement.movement_type = movement_type

    db.add(movement)
    await db.flush()  # assigns movement.id and Python-side defaults (operation_date)

    await outbox_service.enqueue_event(
        db,
        aggregate_type="material_movement",
        aggregate_id=movement.id,
        event_type=movement_type.code,
        payload={
            "movement_id": movement.id,
            "movement_type": movement_type.code,
            "material_id": material.id,
            "warehouse_id": warehouse.id,
            "location_id": location.id,
            "quantity": float(movement.quantity),
            "operation_date": movement.operation_date.isoformat(),
        },
    )

    # One commit for everything - all or nothing :)
    await db.commit()
    return movement


async def list_movements(db: AsyncSession, limit: int, offset: int) -> list[MaterialMovement]:
    stmt = (
        select(MaterialMovement)
        .options(*_MOVEMENT_LOAD_OPTIONS)
        .order_by(MaterialMovement.id.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_movement(db: AsyncSession, movement_id: int) -> MaterialMovement:
    stmt = (
        select(MaterialMovement)
        .options(*_MOVEMENT_LOAD_OPTIONS)
        .where(MaterialMovement.id == movement_id)
    )
    movement = (await db.execute(stmt)).scalar_one_or_none()
    if movement is None:
        raise NotFoundError(f"Movement {movement_id} not found")
    return movement


def to_movement_out(movement: MaterialMovement) -> MovementOut:
    """Maps an ORM MaterialMovement (with relationships loaded) to the API schema."""
    return MovementOut(
        id=movement.id,
        material=MaterialBrief.model_validate(movement.material),
        warehouse=WarehouseBrief.model_validate(movement.warehouse),
        location=LocationBrief.model_validate(movement.location),
        movement_type=movement.movement_type.code,
        quantity=float(movement.quantity),
        operation_date=movement.operation_date,
        employee=EmployeeBrief.model_validate(movement.employee),
        unit_price=float(movement.unit_price) if movement.unit_price is not None else None,
        comment=movement.comment,
        document_ref=movement.document_ref,
    )
