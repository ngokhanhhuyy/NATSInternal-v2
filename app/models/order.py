from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from app.data import Base
from app.extensions.date_time import Time
from app.errors import DataValidationError
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.order_item import OrderItem
    from app.models.order_payment import OrderPayment

class Order(Base):
    # Table name
    __tablename__ = "order"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    customerID: Mapped[int] = mapped_column(
        "customer_id",
        Integer,
        ForeignKey("customer.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False)
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False)
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime, nullable=False)
    orderedDateTime: Mapped[datetime] = mapped_column("ordered_datetime", DateTime, nullable=False)
    deliveredDateTime: Mapped[datetime] = mapped_column("delivered_datetime", DateTime, nullable=False)
    shipmentFee: Mapped[int] = mapped_column("shipment_fee", Integer, nullable=False, default=0)
    shipmentFeeIncluded: Mapped[bool] = mapped_column(
        "shipment_fee_included",
        Boolean,
        nullable=False,
        default=False)
    note: Mapped[str] = mapped_column("note", String(255))

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="orders")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
    payments: Mapped[List["OrderPayment"]] = relationship("OrderPayment", back_populates="order")

    def __init__(self):
        self.createdDateTime = Time.getCurrentDateTime()

    @validates("orderedDateTime")
    def orderedDateTimeValidating(self, _key: str, value: datetime):
        if self.deliveredDateTime is not None and value > self.deliveredDateTime:
            raise DataValidationError(
                modelName="order",
                fieldName="orderedDateTime",
                rule="Thời gian đặt hàng không thể lớn hơn thời gian giao hàng.")
        return value
    
    @validates("deliveredDateTime")
    def deliveredDateTimeValidating(self, _key: str, value: datetime):
        if self.orderedDateTime is not None and value < self.orderedDateTime:
            raise DataValidationError(
                modelName="order",
                fieldName="orderedDateTime",
                rule="Thời gian giao hàng không thể nhỏ hơn thời gian đặt hàng.")
        return value
    
    @validates("shipmentFee")
    def shipmentFeeValidating(self, _key: str, value: int):
        if value < 0:
            raise DataValidationError(
                modelName="order",
                fieldName="shipmentFee",
                rule="Phí giao hàng không thể nhỏ hơn 0.")
        return value

    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="order",
                    fieldName="note",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""
