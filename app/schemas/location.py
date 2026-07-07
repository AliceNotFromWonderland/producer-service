from pydantic import BaseModel, ConfigDict


class LocationBrief(BaseModel):
    """
    Minimal location representation, used when nested inside other
    responses (e.g. movements).
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
