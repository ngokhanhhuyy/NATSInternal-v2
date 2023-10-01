from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.errors import DataValidationError
from datetime import datetime
from app.extensions.date_time import Time
from enum import StrEnum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User

class Announcement(Base):
    # Category enumeration
    class Categories(StrEnum):
        Announcement = "Thông báo"
        News = "Tin tức"
        Warning = "Cảnh báo"

    # Table name
    __tablename__ = "announcement"

    # Model Attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    category: Mapped[str] = mapped_column(
        "category",
        Enum(Categories, name="announcementCategories"),
        nullable=False,
        default=Categories.Announcement.value)
    title: Mapped[str] = mapped_column("title", String(80))
    content: Mapped[str] = mapped_column("content", String(5000))
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime)
    startingDateTime: Mapped[datetime] = mapped_column("starting_datetime", DateTime)
    endingDateTime: Mapped[datetime] = mapped_column("endingDateTime", DateTime)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="announcements")

    def __init__(self):
        self.createdDateTime = Time.getCurrentDateTime()
        self.startingDateTime = self.createdDateTime

    @validates("category")
    def categoryValidating(self, _key: str, value: str | Categories) -> Categories:
        if isinstance(value, self.Categories):
            return value
        return self.Categories(value)
    
    @validates("title")
    def titleValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="announcement",
                fieldName="title",
                rule="Tiêu đề không được bỏ trống.")
        if len(value) > 80:
            raise DataValidationError(
                modelName="announcement",
                fieldName="title",
                rule="Tiêu đề chỉ được chứa tối đa 80 ký tự.")
        return value
    
    @validates("content")
    def contentValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 5000:
                raise DataValidationError(
                    modelName="announcement",
                    fieldName="title",
                    rule="Nội dung chỉ được chứa tối đa 5000 ký tự.")
            return value
        return ""
        
