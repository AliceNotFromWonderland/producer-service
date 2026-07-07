from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MovementType(Base):
    __tablename__ = "movement_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
