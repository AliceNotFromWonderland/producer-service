from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockBalance(Base):
    __tablename__ = "stock_balance"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_stock_balance_quantity_non_negative"),
    )

    material_id: Mapped[int] = mapped_column(ForeignKey("material.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), primary_key=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    material: Mapped["Material"] = relationship()
    location: Mapped["Location"] = relationship()
