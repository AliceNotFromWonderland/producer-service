from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    warehouses: Mapped[list["Warehouse"]] = relationship(back_populates="organization")
    employees: Mapped[list["Employee"]] = relationship(back_populates="organization")
