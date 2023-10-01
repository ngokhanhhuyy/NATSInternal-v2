from __future__ import annotations
from sqlalchemy import Integer, String, DateTime, event
from sqlalchemy.orm import validates, relationship, Mapped, mapped_column
from app.data import Base
from app.errors import DataValidationError
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.product import Product

class ProductCategory(Base):
    # Table name
    __tablename__ = "product_category"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("name", String(30), unique=True)
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime)
    
    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")
    
    def __init__(self):
        self.createdDateTime = datetime.now()

    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName=ProductCategory.__tablename__,
                fieldName="name",
                rule="Tên không được để trống.")
        if len(value) > 30:
            raise DataValidationError(
                modelName=ProductCategory.__tablename__,
                fieldName="name",
                rule="Tên chỉ được chứa tối đa 30 ký tự.")
        return value
