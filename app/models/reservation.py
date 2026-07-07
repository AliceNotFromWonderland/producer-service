from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reservation(Base):
    __tablename__ = "reservation"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_reservation_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("material.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)

    material: Mapped["Material"] = relationship()
    location: Mapped["Location"] = relationship()
    employee: Mapped["Employee"] = relationship()
