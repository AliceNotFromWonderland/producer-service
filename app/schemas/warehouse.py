from pydantic import BaseModel, ConfigDict


class WarehouseCreate(BaseModel):
    name: str
    organization_id: int


class WarehouseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    organization_id: int


class WarehouseBrief(BaseModel):
    """Minimal warehouse representation, used when nested inside other responses (e.g. movements)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
