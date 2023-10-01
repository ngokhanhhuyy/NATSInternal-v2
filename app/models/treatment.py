from __future__ import annotations
from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, Session
from app.data import Base
from app.errors import DataValidationError
from datetime import datetime
from app.extensions.date_time import Time
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.treatment_session import TreatmentSession
    from app.models.treatment_payment import TreatmentPayment

class Treatment(Base):
    # Table name
    __tablename__ = "treatment"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    customerID: Mapped[int] = mapped_column(
        "customer_id",
        Integer,
        ForeignKey("customer.id", ondelete="CASCADE", onupdate="CASCADE"))
    orderedDateTime: Mapped[datetime] = mapped_column("ordered_datetime", DateTime)
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime)
    updatedDateTime: Mapped[datetime] = mapped_column("updated_datetime", DateTime)
    price: Mapped[int] = mapped_column("price", Integer, default=0)
    vatFactor: Mapped[float] = mapped_column("vat_factor", Numeric, default=0.1)
    note: Mapped[str] = mapped_column("note", String(255))

    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="treatments")
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="treatments")
    sessions: Mapped[List["TreatmentSession"]] = relationship(
        "TreatmentSession",
        back_populates="treatment")
    payments: Mapped[List["TreatmentPayment"]] = relationship(
        "TreatmentPayment",
        back_populates="treatment")

    def __init__(self):
        self.orderedDateTime = Time.getCurrentDateTime()
        self.createdDateTime = Time.getCurrentDateTime()
        self.updatedDateTime = Time.getCurrentDateTime()

    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="treatment",
                    fieldName="note",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""
    
def adjustingUpdatedDateTime(session: Session, _context, _instance):
    for obj in session.dirty:
        if isinstance(obj, Treatment):
            treatment = obj
            treatment.updatedDateTime = Time.getCurrentDateTime()
event.listens_for(Session, "before_flush", adjustingUpdatedDateTime)