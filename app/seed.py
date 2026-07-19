import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Category, Employee, Location, MovementType, Organization, Unit, Warehouse

MOVEMENT_TYPES = [
    ("INCOME", "Приход"),
    ("ISSUE", "Выдача"),
    ("INVOLVE", "Вовлечение"),
    ("SALE", "Продажа"),
    ("WRITE_OFF", "Списание"),
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        for code, name in MOVEMENT_TYPES:
            existing = (
                await db.execute(select(MovementType).where(MovementType.code == code))
            ).scalar_one_or_none()
            if existing is None:
                db.add(MovementType(code=code, name=name))
        await db.commit()

        org = (
            await db.execute(select(Organization).where(Organization.code == "DEMO"))
        ).scalar_one_or_none()
        if org is None:
            org = Organization(name="Demo Company", code="DEMO")
            db.add(org)
            await db.commit()

        unit = (await db.execute(select(Unit).where(Unit.name == "шт"))).scalar_one_or_none()
        if unit is None:
            unit = Unit(name="шт")
            db.add(unit)
            await db.commit()

        category = (
            await db.execute(select(Category).where(Category.name == "General"))
        ).scalar_one_or_none()
        if category is None:
            category = Category(name="General")
            db.add(category)
            await db.commit()

        employee = (
            await db.execute(
                select(Employee).where(Employee.last_name == "Ivanov", Employee.first_name == "Ivan")
            )
        ).scalar_one_or_none()
        if employee is None:
            employee = Employee(
                last_name="Ivanov",
                first_name="Ivan",
                middle_name="Ivanovich",
                organization_id=org.id,
                department="Warehouse",
            )
            db.add(employee)
            await db.commit()

        warehouse = (
            await db.execute(
                select(Warehouse).where(
                    Warehouse.organization_id == org.id, Warehouse.name == "Main warehouse"
                )
            )
        ).scalar_one_or_none()
        if warehouse is None:
            warehouse = Warehouse(name="Main warehouse", organization_id=org.id)
            db.add(warehouse)
            await db.commit()

        location = (
            await db.execute(
                select(Location).where(
                    Location.warehouse_id == warehouse.id, Location.name == "Cabinet A1"
                )
            )
        ).scalar_one_or_none()
        if location is None:
            location = Location(warehouse_id=warehouse.id, name="Cabinet A1")
            db.add(location)
            await db.commit()

        print("Seed completed.")
        print(f"  organization_id = {org.id}")
        print(f"  unit_id         = {unit.id}")
        print(f"  category_id     = {category.id}")
        print(f"  employee_id     = {employee.id}")
        print(f"  warehouse_id    = {warehouse.id}")
        print(f"  location_id     = {location.id}")


if __name__ == "__main__":
    asyncio.run(seed())
