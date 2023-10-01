from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.data import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.permission import Permission

class UserPermission(Base):
    # Table name
    __tablename__ = "user_permission"

    # Model attributes
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True)
    permissionID: Mapped[int] = mapped_column(
        "permission_id",
        Integer,
        ForeignKey("permission.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True)
    approvalRequired: Mapped[bool] = mapped_column("approval_required", Boolean)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="userPermissions")
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="userPermissions")
    