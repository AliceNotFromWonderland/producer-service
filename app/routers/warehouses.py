from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import WarehouseCreate, WarehouseOut
from app.services import warehouse_service

router = APIRouter(prefix="/v1/warehouses", tags=["warehouses"])


@router.post("", response_model=WarehouseOut, status_code=201)
async def create_warehouse(payload: WarehouseCreate, db: AsyncSession = Depends(get_db)):
    return await warehouse_service.create_warehouse(db, payload)
