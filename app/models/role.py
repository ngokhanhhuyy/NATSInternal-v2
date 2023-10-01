from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import validates, relationship, Mapped, mapped_column
from app.data import Base
from app.models.user_role import userRole
from app.errors import DataValidationError
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role_permission import RolePermission

class Role(Base):
    # Table name
    __tablename__ = "role"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("name", String(20), unique=True)

    # Relationship
    users: Mapped[List["User"]] = relationship(secondary=userRole, back_populates="roles")
    rolePermissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="role")
    
    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 20:
                raise DataValidationError(
                    modelName="role",
                    fieldName="name",
                    rule="Tên chỉ được chứa tối đa 20 ký tự.")
            return value
        raise DataValidationError(
            modelName="role",
            fieldName="name",
            rule="Tên không được để trống.")