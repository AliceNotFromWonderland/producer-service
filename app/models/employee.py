from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"), nullable=False)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="employees")
