from __future__ import annotations
from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, Session
from sqlalchemy.orm.attributes import get_history, History
from app.data import getDatabaseSession
from app.data import Base
from app.models.product_price_history import ProductPriceHistory
from app.models.photo import Photo
from app.extensions.date_time import Time
from app.errors import DataValidationError
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.brand import Brand
    from app.models.product_category import ProductCategory
    from app.models.product_price_history import ProductPriceHistory
    from app.models.supply_item import SupplyItem
    from app.models.order_item import OrderItem
    from app.models.treatment_item import TreatmentItem

class Product(Base):
    # Table name
    __tablename__ = "product"
    
    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    brandID: Mapped[int] = mapped_column(
        "brand_id",
        Integer,
        ForeignKey("brand.id", ondelete="SET NULL", onupdate="CASCADE"))
    categoryID: Mapped[int] = mapped_column(
        "category_id",
        Integer,
        ForeignKey("product_category.id", ondelete="SET NULL", onupdate="CASCADE"))
    description: Mapped[str] = mapped_column(String(1000))
    unit: Mapped[str] = mapped_column(String(12))
    price: Mapped[int] = mapped_column("price", Integer)
    vatFactor: Mapped[float] = mapped_column("vat_factor", Numeric)
    isForRetail: Mapped[bool] = mapped_column("is_for_retail", Boolean, default=True)
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime)
    updatedDateTime: Mapped[datetime] = mapped_column("updated_datetime", DateTime)

    # Relationship
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    category: Mapped["ProductCategory"] = relationship("ProductCategory", back_populates="products")
    prices: Mapped[List["ProductPriceHistory"]] = relationship("ProductPriceHistory", back_populates="product")
    photos: Mapped[List["Photo"]] = relationship("Photo", back_populates="product")
    supplyItems: Mapped[List["SupplyItem"]] = relationship("SupplyItem", back_populates="product")
    orderItems: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
    treatmentItems: Mapped[List["TreatmentItem"]] = relationship("TreatmentItem", back_populates="product")

    def __init__(self):
        self.createdDateTime = Time.getCurrentDateTime()
        self.updatedDateTime = Time.getCurrentDateTime()

    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName=Product.__tablename__,
                fieldName="name",
                rule="Không được để trống.")
        if len(value) > 50:
            raise DataValidationError(
                modelName=Product.__tablename__,
                fieldName="name",
                rule="Chỉ có thể chứa tối đa 50 ký tự.")
        return value
        
    @validates("description")
    def descriptionValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 1000:
                raise DataValidationError(
                    modelName=Product.__tablename__,
                    fieldName="description",
                    rule="Mô tả chỉ được chứa tối đa 1000 ký tự.")
            return value
        return ""
        
    @validates("unit")
    def unitValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="product",
                fieldName="unit",
                rule="Đơn vị không được để trống")
        if len(value) > 12:
            raise DataValidationError(
                modelName="product",
                fieldName="unit",
                rule="Đơn vị chỉ được chứa tối đa 12 ký tự")
        return value

def adjustingUpdatedDateTime(session: Session, _context, _instance):
    tempIndex = 0
    for obj in session.dirty:
        if isinstance(obj, Product):
            product = obj
            product.updatedDateTime = Time.getCurrentDateTime()
            product.tempIndex: int = tempIndex 
            priceHistory: History = get_history(product, "publishedPrice")
            if priceHistory.has_changes():
                priceHistory = ProductPriceHistory()
                priceHistory.productID = product.id
                priceHistory.price = product.price
                priceHistory.productTempIndex = tempIndex
                session.add(priceHistory)
            tempIndex += 1            
event.listen(Session, "before_flush", adjustingUpdatedDateTime)

def loggingPriceHistory(session: Session, flush_context):
    for object1 in session.dirty:
        if isinstance(object1, ProductPriceHistory):
            priceHistory = object1
            for object2 in session.dirty:
                if isinstance(object2, Product):
                    product: Product = object2
                    if priceHistory.productTempIndex == product.tempIndex:
                        priceHistory.productID = product.id
                        del priceHistory.productTempIndex
                        del product.tempIndex
event.listen(Session, "after_flush", loggingPriceHistory)
                
