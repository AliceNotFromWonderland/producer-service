from typing import Optional

from pydantic import BaseModel, ConfigDict


class EmployeeBrief(BaseModel):
    """Minimal employee representation, used when nested inside other responses (e.g. movements)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
