from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models import Organization, Warehouse
from app.schemas import WarehouseCreate


async def create_warehouse(db: AsyncSession, payload: WarehouseCreate) -> Warehouse:
    # `name` and `organization_id` presence is already guaranteed by
    # WarehouseCreate (both required, no default) — Pydantic rejects a
    # request missing either before this function ever runs; see
    # error_handlers.py for how that maps to 400.
    organization = await db.get(Organization, payload.organization_id)
    if organization is None:
        raise NotFoundError(f"Organization {payload.organization_id} not found")

    # Uniqueness is scoped to the organization: two different companies are
    # allowed to each have a warehouse called e.g. "Main warehouse".
    exists_stmt = select(Warehouse).where(
        Warehouse.organization_id == payload.organization_id,
        Warehouse.name == payload.name,
    )
    exists = (await db.execute(exists_stmt)).scalar_one_or_none()
    if exists:
        raise ConflictError({"detail": "Warehouse with this name already exists"})

    warehouse = Warehouse(name=payload.name, organization_id=payload.organization_id)
    db.add(warehouse)
    await db.commit()
    return warehouse
