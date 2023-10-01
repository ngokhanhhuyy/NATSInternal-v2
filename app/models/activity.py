from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from app.data import Base
from app.errors import DataValidationError
from enum import StrEnum, IntEnum, unique
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.activity_request import ActivityRequest
    from app.models.permission import Permission

class Activity(Base):
    @unique
    class Actions(StrEnum):
        GettingApiKey = "Lấy khoá API"
        GettingJwtKey = "Lấy mã JWT"
        WebLogin = "Đăng nhập trên web"
        Creating = "Tạo"
        Reading = "Đọc"
        Updating = "Sửa"
        Deleting = "Xoá"

    @unique
    class ImportanceLevel(IntEnum):
        NotImportant = 0
        Low = 1
        Medium = 2
        High = 3
        VeryHigh = 4
    
    # Table name
    __tablename__ = "activity"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    action: Mapped[str] = mapped_column("action", Enum(Actions))
    permissionID: Mapped[int] = mapped_column(
        "permission_id",
        Integer,
        ForeignKey("permission.id", ondelete="CASCADE", onupdate="CASCADE"))
    objectType: Mapped[str] = mapped_column("object_type", String(20))
    objectID: Mapped[int | None] = mapped_column("object_id", Integer)
    oldData: Mapped[dict | None] = mapped_column("old_data", JSON)
    newData: Mapped[dict | None] = mapped_column("new_data", JSON)
    isFinished: Mapped[bool] = mapped_column("is_finished", Boolean)
    isForDeveloper: Mapped[bool] = mapped_column("is_for_developer", Boolean)
    importanceLevel: Mapped[int | None] = mapped_column(
        "importance_level",
        Enum(ImportanceLevel, name="importanceLevel"),
        default=ImportanceLevel.NotImportant)
    note: Mapped[str] = mapped_column("note", String(255))
    
    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        uselist=False,
        back_populates="activities")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="activities")
    request: Mapped["ActivityRequest"] = relationship("ActivityRequest", back_populates="activity")
    
    @validates("action")
    def actionValidating(self, _key: str, value: str) -> str:
        if isinstance(value, self.Actions):
            return value.value
        if value not in [action.value for action in self.Actions]:
            raise ValueError
        return value
    
    @validates("objectType")
    def objectTypeValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 20:
                raise DataValidationError(
                    modelName="activity",
                    fieldName="objectName",
                    rule="Loại đối tượng (objectType) chỉ đước chứa tối đa 20 ký tự.")
            return value
        return ""
    
    @validates("importanceLevel")
    def importanceLevelValidating(self, _key: str, value: str | ImportanceLevel) -> ImportanceLevel:
        if isinstance(value, str):
            return self.ImportanceLevel(value)
        return value
    
    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="activity",
                    fieldName="objectName",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""