from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.employee import EmployeeBrief
from app.schemas.location import LocationBrief
from app.schemas.material import MaterialBrief
from app.schemas.warehouse import WarehouseBrief


class MovementCreate(BaseModel):
    """Shared request shape for income / issue / write-off."""
    material_id: int
    warehouse_id: int
    location_id: int
    quantity: float
    employee_id: int
    unit_price: Optional[float] = None
    comment: Optional[str] = None
    document_ref: Optional[str] = None


class MovementOut(BaseModel):
    id: int
    material: MaterialBrief
    warehouse: WarehouseBrief
    location: LocationBrief
    movement_type: str
    quantity: float
    operation_date: datetime
    employee: EmployeeBrief
    unit_price: Optional[float] = None
    comment: Optional[str] = None
    document_ref: Optional[str] = None
