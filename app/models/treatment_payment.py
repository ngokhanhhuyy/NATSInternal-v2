from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.errors import DataValidationError
from app.extensions.date_time import Time
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.treatment import Treatment

class TreatmentPayment(Base):
    # Table name
    __tablename__ = "treatment_payment"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    treatmentID: Mapped[int] = mapped_column(
        "treatment_id",
        Integer,
        ForeignKey("treatment.id", ondelete="CASCADE", onupdate="CASCADE"))
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    paidAmount: Mapped[int] = mapped_column("paid_amount", Integer)
    paidDateTime: Mapped[int] = mapped_column("paid_datetime", DateTime)
    note: Mapped[str] = mapped_column("note", String(255))

    # Relationship
    treatment: Mapped["Treatment"] = relationship("Treatment", back_populates="payments")
    user: Mapped["User"] = relationship("User", back_populates="treatmentPayments")

    def __init__(self):
        self.paidDateTime = Time.getCurrentDateTime()

    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="treatmentPayment",
                    fieldName="note",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""
