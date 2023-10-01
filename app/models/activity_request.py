from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from datetime import datetime
from app.data import Base
from app.errors import DataValidationError
from enum import StrEnum, unique
from typing import List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.activity import Activity

class ActivityRequest(Base):
    # Status enumeration
    @unique
    class Statuses(StrEnum):
        Requested = "Đã gửi yêu cầu"
        Rejected = "Đã bị từ chối"
        Approved = "Đã chấp thuận"

    # Table name
    __tablename__ = "activity_request"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    activityID: Mapped[int] = mapped_column(
        "activity_id",
        Integer,
        ForeignKey("activity.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False)
    userNote: Mapped[str] = mapped_column("user_note", String(255))
    status: Mapped[str] = mapped_column("status", Enum(Statuses), nullable=False, default=Statuses.Requested)
    reviewerID: Mapped[int | None] = mapped_column(
        "reviewer_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    reviewerNote: Mapped[str] = mapped_column("reviewer_note", String(255))
    reviewedDateTime: Mapped[datetime | None] = mapped_column("reviewed_datetime", DateTime)

    # Relationship
    activity: Mapped["Activity"] = relationship("Activity", uselist=False, back_populates="request")
    reviewer: Mapped["User"] = relationship("User", back_populates="reviewedRequests")

    @validates("status")
    def statusValidating(self, _key: str, value: str | Statuses) -> str:
        if isinstance(value, self.Statuses):
            return value.value
        if value not in [status.value for status in self.Statuses]:
                raise ValueError
        return value
    
    @validates("userNote")
    def userNoteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="activityRequest",
                    fieldName="userNote",
                    rule="Ghi chú của nhân viên chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""
    
    @validates("reviewerNote")
    def reviewerNoteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="activityRequest",
                    fieldName="reviewerNote",
                    rule="Ghi chú của người duyệt chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""