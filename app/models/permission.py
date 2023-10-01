from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import validates, relationship, Mapped, mapped_column
from app.data import Base
from app.errors import DataValidationError
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.role_permission import RolePermission
    from app.models.user_permission import UserPermission
    from app.models.activity import Activity

class Permission(Base):
    # Table name
    __tablename__ = "permission"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("name", String(70), unique=True)

    # Relationships
    rolePermissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission")
    userPermissions: Mapped[List["UserPermission"]] = relationship(
        "UserPermission",
        back_populates="permission")
    activities: Mapped[List["Activity"]] = relationship(
        "Activity",
        back_populates="permission")
    
    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="permission",
                fieldName="name",
                rule="Tên không được để trống.")
        if len(value) > 70:
            raise DataValidationError(
                modelName="permission",
                fieldName="name",
                rule="Tên chỉ được chứa tối đa 70 ký tự.")
        return value