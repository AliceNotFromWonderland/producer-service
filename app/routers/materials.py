from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    MaterialCreate,
    MaterialListItem,
    MaterialOut,
    MovementCreate,
    MovementOut,
)
from app.services import material_service, movement_service

MAX_PAGE_SIZE = 1000

router = APIRouter(prefix="/v1/materials", tags=["materials"])


@router.post("", response_model=MaterialOut, status_code=201)
async def create_material(payload: MaterialCreate, db: AsyncSession = Depends(get_db)):
    return await material_service.create_material(db, payload)


@router.get("", response_model=list[MaterialListItem])
async def list_materials(
    limit: int = Query(50, gt=0, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await material_service.list_materials(db, limit, offset)


@router.post("/income", response_model=MovementOut, status_code=201)
async def create_income(payload: MovementCreate, db: AsyncSession = Depends(get_db)):
    movement = await movement_service.create_income(db, payload)
    return movement_service.to_movement_out(movement)


@router.post("/issue", response_model=MovementOut, status_code=201)
async def create_issue(payload: MovementCreate, db: AsyncSession = Depends(get_db)):
    movement = await movement_service.create_issue(db, payload)
    return movement_service.to_movement_out(movement)


@router.post("/write-off", response_model=MovementOut, status_code=201)
async def create_write_off(payload: MovementCreate, db: AsyncSession = Depends(get_db)):
    movement = await movement_service.create_write_off(db, payload)
    return movement_service.to_movement_out(movement)


@router.get("/movements", response_model=list[MovementOut])
async def list_movements(
    limit: int = Query(50, gt=0, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    movements = await movement_service.list_movements(db, limit, offset)
    return [movement_service.to_movement_out(m) for m in movements]


@router.get("/movements/{movement_id}", response_model=MovementOut)
async def get_movement(movement_id: int, db: AsyncSession = Depends(get_db)):
    movement = await movement_service.get_movement(db, movement_id)
    return movement_service.to_movement_out(movement)
