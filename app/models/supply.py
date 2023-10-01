from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.errors import DataValidationError
from app.extensions.date_time import Time
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.supply_item import SupplyItem

class Supply(Base):
    # Table name
    __tablename__ = "supply"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    orderedDateTime: Mapped[datetime] = mapped_column("ordered_datetime", DateTime)
    arrivedDateTime: Mapped[datetime] = mapped_column("arrived_datetime", DateTime)
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="SET DEFAULT", onupdate="CASCADE"),
        default=0)
    shipmentFee: Mapped[int] = mapped_column("shipment_free", Integer, default=0)
    paidAmount: Mapped[int] = mapped_column("paid_amount", Integer, default=0)
    note: Mapped[str] = mapped_column("note", String(255))

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="supplies")
    items: Mapped[List["SupplyItem"]] = relationship("SupplyItem", back_populates="supply")

    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="supply",
                    fieldName="note",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""
