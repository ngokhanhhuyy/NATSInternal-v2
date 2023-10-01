from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship, Mapped, mapped_column
from app.data import Base
from app.errors import DataValidationError
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.brand import Brand

class Country(Base):
    # Table name
    __tablename__ = "country"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("name", String(40), unique=True)
    code: Mapped[str] = mapped_column("code", String(3), unique=True)
    
    # Relationships
    brands: Mapped[List["Brand"]] = relationship("Brand", back_populates="country")

    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="country",
                fieldName="name",
                rule="Tên quốc gia không được để trống.")
        if len(value) > 40:
            raise DataValidationError(
                modelName="country",
                fieldName="name",
                rule="Tên quốc gia chỉ được chứa 40 ký tự.")
        return value
    
    @validates("code")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) != 3:
            raise DataValidationError(
                modelName="country",
                fieldName="name",
                rule="Mã quốc gia phải chứa 3 chữ cái.")
        if not value.isalpha():
            raise DataValidationError(
                modelName="country",
                fieldName="name",
                rule="Mã quốc gia chỉ được chứa chữ cái.")
        return value