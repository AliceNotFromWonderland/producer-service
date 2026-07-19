from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models import Category, Material, StockBalance, Unit
from app.schemas import MaterialCreate, MaterialListItem


async def create_material(db: AsyncSession, payload: MaterialCreate) -> Material:
    unit = await db.get(Unit, payload.unit_id)
    if unit is None:
        raise NotFoundError(f"Unit {payload.unit_id} not found")

    if payload.category_id is not None:
        category = await db.get(Category, payload.category_id)
        if category is None:
            raise NotFoundError(f"Category {payload.category_id} not found")

    exists_stmt = select(Material).where(Material.article == payload.article)
    exists = (await db.execute(exists_stmt)).scalar_one_or_none()
    if exists:
        raise ConflictError({"detail": "Material with this article already exists"})

    material = Material(
        article=payload.article,
        name=payload.name,
        unit_id=payload.unit_id,
        category_id=payload.category_id,
        description=payload.description,
    )
    db.add(material)
    await db.commit()
    return material


async def list_materials(db: AsyncSession, limit: int, offset: int) -> list[MaterialListItem]:
    stmt = (
        select(
            Material,
            Unit.name.label("unit_name"),
            Category.name.label("category_name"),
            func.coalesce(func.sum(StockBalance.quantity), 0).label("total_quantity"),
        )
        .join(Unit, Material.unit_id == Unit.id)
        .outerjoin(Category, Material.category_id == Category.id)
        .outerjoin(StockBalance, StockBalance.material_id == Material.id)
        .group_by(Material.id, Unit.name, Category.name)
        .order_by(Material.id)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        MaterialListItem(
            id=material.id,
            article=material.article,
            name=material.name,
            unit_name=unit_name,
            category_name=category_name,
            total_quantity=float(total_quantity),
        )
        for material, unit_name, category_name, total_quantity in rows
    ]
