from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.data import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.permission import Permission

class RolePermission(Base):
    # Table name
    __tablename__ = "role_permission"

    # Model attributes
    roleID: Mapped[int] = mapped_column(
        "role_id",
        Integer,
        ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True)
    permissionID: Mapped[int] = mapped_column(
        "permission_id",
        Integer,
        ForeignKey("permission.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True)
    approvalRequired: Mapped[bool] = mapped_column("approval_required", Boolean)

    # Relationship
    role: Mapped["Role"] = relationship("Role", back_populates="rolePermissions")
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="rolePermissions")
    