from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.extensions.date_time import Time
from app.errors import DataValidationError
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.expense import Expense

class ExpensePayee(Base):
    # Table name
    __tablename__ = "expense_payee"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("name", String(100), unique=True)
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime, nullable=False)

    # Relationship
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="payee")

    def __init__(self):
        super().__init__()
        self.createdDateTime = Time.getCurrentDateTime()

    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 100:
                raise DataValidationError(
                    modelName="expensePayee",
                    fieldName="name",
                    rule="Tên người/công ty được thanh toán chi phí chỉ được chứa tối đa 100 ký tự.")
            return value
        return ""

