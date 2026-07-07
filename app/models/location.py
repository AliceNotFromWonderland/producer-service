from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Location(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("location.id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    warehouse: Mapped["Warehouse"] = relationship(back_populates="locations")
    parent: Mapped["Location | None"] = relationship(remote_side="Location.id")
