from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouse"
    __table_args__ = (
        # Uniqueness is scoped to the organization —
        # two different companies may each have a warehouse called e.g. "Main warehouse".
        UniqueConstraint("organization_id", "name", name="uq_warehouse_org_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="warehouses")
    locations: Mapped[list["Location"]] = relationship(back_populates="warehouse")
