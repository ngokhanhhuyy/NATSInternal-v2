from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.errors import DataValidationError
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:         
    from app.models.user import User
    from app.models.expense_payee import ExpensePayee
    from app.models.expense_category import ExpenseCategory
                          
class Expense(Base):      
    # Table name          
    __tablename__ = "expense"
                          
    # Model attributes    
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    payeeID: Mapped[int | None] = mapped_column(
        "payee_id",       
        Integer,          
        ForeignKey("expense_payee.id", ondelete="SET NULL", onupdate="CASCADE"))
    userID: Mapped[int] = mapped_column(
        "user_id",                   
        Integer,                     
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    categoryID: Mapped[int | None] = mapped_column(
        "category_id",                              
        Integer,                                    
        ForeignKey("expense_category.id", ondelete="CASCADE", onupdate="CASCADE"))
    amount: Mapped[int] = mapped_column("amount", Integer)
    vatFactor: Mapped[float] = mapped_column("vat_factor", Numeric, default=0.1)
    paidDateTime: Mapped[datetime]  = mapped_column("paid_datetime", DateTime)
    note: Mapped[str] = mapped_column("note", String(255))
                                                    
    # Relationship                                  
    payee: Mapped["ExpensePayee"] = relationship("ExpensePayee", back_populates="expenses")
    user: Mapped["User"] = relationship("User", back_populates="expenses")
    category: Mapped["ExpenseCategory"] = relationship("ExpenseCategory", back_populates="expenses")
                                                    
    @validates("note")                              
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():    
            if len(value) > 255:                    
                raise DataValidationError(         
                    modelName="expense",            
                    fieldName="note",               
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""
