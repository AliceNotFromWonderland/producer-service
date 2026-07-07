from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Material(Base):
    __tablename__ = "material"

    id: Mapped[int] = mapped_column(primary_key=True)
    article: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("unit.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    unit: Mapped["Unit"] = relationship()
    category: Mapped["Category | None"] = relationship()
