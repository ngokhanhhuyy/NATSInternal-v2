from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.errors import DataValidationError
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:     
    from app.models.expense import Expense
                      
class ExpenseCategory(Base):
    # Table name      
    __tablename__ = "expense_category"
                      
    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("name", String(30))
                      
    # Relationship    
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="category")
                      
    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="expensePayee",
                fieldName="name",
                rule="Tên phân loại không được để trống.")
        if len(value) > 100:
            raise DataValidationError(
                modelName="expensePayee",
                fieldName="name",
                rule="Tên phân loại chi phí chỉ được chứa tối đa 30 ký tự.")
        return value
                  
                  