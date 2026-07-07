from typing import Optional

from pydantic import BaseModel, ConfigDict


class MaterialCreate(BaseModel):
    article: str
    name: str
    unit_id: int
    category_id: Optional[int] = None
    description: Optional[str] = None


class MaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article: str
    name: str
    unit_id: int
    category_id: Optional[int] = None
    description: Optional[str] = None


class MaterialListItem(BaseModel):
    id: int
    article: str
    name: str
    unit_name: str
    category_name: Optional[str] = None
    total_quantity: float


class MaterialBrief(BaseModel):
    """Minimal material representation, used when nested inside other responses (e.g. movements)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    article: str
    name: str
