from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MaterialMovement(Base):
    __tablename__ = "material_movement"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_material_movement_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("material.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), nullable=False)
    movement_type_id: Mapped[int] = mapped_column(ForeignKey("movement_type.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    operation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)
    unit_price: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    material: Mapped["Material"] = relationship()
    warehouse: Mapped["Warehouse"] = relationship()
    location: Mapped["Location"] = relationship()
    movement_type: Mapped["MovementType"] = relationship()
    employee: Mapped["Employee"] = relationship()
