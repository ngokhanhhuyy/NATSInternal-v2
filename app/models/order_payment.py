from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.errors import DataValidationError
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.user import User

class OrderPayment(Base):
    # Table name
    __tablename__ = "order_payment"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    orderID: Mapped[int] = mapped_column(
        "order_id",
        Integer,
        ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"))
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    amount: Mapped[int] = mapped_column("amount", Integer)
    paidDateTime: Mapped[datetime] = mapped_column("paid_datetime", DateTime)
    note: Mapped[str] = mapped_column("note", String(255))

    # Relationship
    order: Mapped["Order"] = relationship("Order", back_populates="payments")
    user: Mapped["User"] = relationship("User", back_populates="orderPayments")

    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="orderPayment",
                    fieldName="note",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""


