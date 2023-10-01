from __future__ import annotations
from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.orm import relationship, validates, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from app.data import Session
from datetime import date, datetime
from app import bcrypt
from app.data import Base
from app.models.user_role import userRole
from app.models.treatment_therapist import treatmentTherapist
from app.errors import DataValidationError
from app.extensions.date_time import Time
from app.enum import Sexes
from typing import Callable, List, TYPE_CHECKING
from enum import StrEnum, unique
from datetime import timedelta
if TYPE_CHECKING:
    from app.models.user_permission import UserPermission
    from app.models.role import Role
    from app.models.activity import Activity
    from app.models.user_session import UserSession
    from app.models.user_api_key import UserApiKey
    from app.models.activity_request import ActivityRequest
    from app.models.supply import Supply
    from app.models.order import Order
    from app.models.order_payment import OrderPayment
    from app.models.expense import Expense
    from app.models.announcement import Announcement
    from app.models.treatment import Treatment
    from app.models.treatment_session import TreatmentSession
    from app.models.treatment_payment import TreatmentPayment
    from app.models.photo import Photo

class User(Base):
    # Status enumeration
    @unique
    class Statuses(StrEnum):
        Undefined = "Không xác định"
        Pending = "Đang chờ kích hoạt"
        Active = "Đang hoạt động"
        Inactive = "Tạm thời ngưng"
        Quit = "Đã nghỉ"

    # Table name
    __tablename__ = "user"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    userName: Mapped[str] = mapped_column("username", String(25), nullable=False, unique=True)
    passwordHash: Mapped[str] = mapped_column("password_hash", String, nullable=False)
    firstName: Mapped[str] = mapped_column("first_name", String(10))
    middleName: Mapped[str] = mapped_column("middle_name", String(20))
    lastName: Mapped[str] = mapped_column("last_name", String(10))
    sex: Mapped[str] = mapped_column("sex", Enum(Sexes), nullable=False)
    birthday: Mapped[date | None] = mapped_column("birthday", Date)
    phone: Mapped[str] = mapped_column("phone", String(15))
    email: Mapped[str] = mapped_column("email", String(255))
    idCardNumber: Mapped[str] = mapped_column("id_card_number", String(12))
    joiningDate: Mapped[date | None] = mapped_column("joining_date", Date)
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime)
    updatedDateTime: Mapped[datetime] = mapped_column("updated_datetime", DateTime)
    status: Mapped[str] = mapped_column(
        "status",
        Enum(Statuses, name="userStatuses"),
        nullable=False)
    note: Mapped[str] = mapped_column("note", String(255))

    # Relationship
    apiKey: Mapped["UserApiKey"] = relationship("UserApiKey", uselist=False, back_populates="user")
    session: Mapped["UserSession"] = relationship("UserSession", uselist=False, back_populates="user")
    photos: Mapped[List["Photo"]] = relationship("Photo", uselist=True, back_populates="user")
    roles: Mapped[List["Role"]] = relationship(secondary=userRole, back_populates="users")
    activities: Mapped[List["Activity"]] = relationship("Activity", back_populates="user")
    reviewedRequests: Mapped[List["ActivityRequest"]] = relationship("ActivityRequest", back_populates="reviewer")
    userPermissions: Mapped[List["UserPermission"]] = relationship("UserPermission", back_populates="user")
    supplies: Mapped[List["Supply"]] = relationship("Supply", back_populates="user")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")
    orderPayments: Mapped[List["OrderPayment"]] = relationship("OrderPayment", back_populates="user")
    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="user")
    announcements: Mapped[List["Announcement"]] = relationship("Announcement", back_populates="user")
    treatments: Mapped[List["Treatment"]] = relationship("Treatment", back_populates="user")
    treatmentPayments: Mapped[List["TreatmentPayment"]] = relationship("TreatmentPayment", back_populates="user")
    treatmentSessions: Mapped[List["TreatmentSession"]] = relationship(secondary=treatmentTherapist, back_populates="therapists")

    def __init__(self):
        super().__init__()
        self.createdDateTime = Time.getCurrentDateTime()
        self.updatedDateTime = Time.getCurrentDateTime()
    
    @validates("userName")
    def userNameValidating(self, _key: str, value: str) -> str:
        if len(value) < 5 or len(value) > 25:
            raise DataValidationError(
                modelName="user",
                fieldName="userName",
                rule="Tên tài khoản phải chứa từ 5 đến 25 ký tự.")
        elif not value.isalnum():
            raise DataValidationError(
                modelName="user",
                fieldName="userName",
                rule="Tên tài khoản chỉ được chứa chữ và số.")
        return value

    @property
    def password(self) -> None:
        raise AttributeError("Password is unreadable attribute.")

    @password.setter
    def password(self, value: str) -> None:
        if len(value) < 6 or len(value) > 20:
            raise DataValidationError(
                modelName="user",
                fieldName="password",
                rule="Mật khẩu phải chứa từ 6 đến 20 ký tự.")
        elif value.isspace():
            raise DataValidationError(
                modelName="user",
                fieldName="password",
                rule="Mật khẩu không hợp lệ.")
        self.passwordHash = bcrypt.generate_password_hash(value).decode("utf-8")
    
    @validates("firstName")
    def firstNameValidating(self, _key: str, value: str) -> str:
        if len(value) != 0 and not value.isspace():
            if len(value) > 10:
                raise DataValidationError(
                    modelName="user",
                    fieldName="firstName",
                    rule="Họ chỉ được chứa tối đa 10 ký tự.")
            return value
        return ""
    
    @validates("middleName")
    def middleNameValidating(self, _key: str, value: str) -> str:
        if len(value) != 0 and not value.isspace():
            if len(value) > 20:
                raise DataValidationError(
                    modelName="user",
                    fieldName="middleName",
                    rule="Tên lót chỉ được chứa tối đa 20 ký tự.")
            return value
        return ""
    
    @validates("lastName")
    def lastNameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="user",
                fieldName="lastName",
                rule="Tên không được để trống.")
        if len(value) > 35:
            raise DataValidationError(
                modelName="customer",
                fieldName="lastName",
                rule="Tên chỉ được chứa tối đa 10 ký tự.")
        return value

    @validates("phone")
    def phoneValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 15:
                raise DataValidationError(
                    modelName="user",
                    fieldName="phone",
                    rule="Số điện thoại chỉ được chứa tối đa 15 ký tự.")
            if not value.isdigit():
                raise DataValidationError(
                    modelName="user",
                    fieldName="phone",
                    rule="Số điện thoại chỉ được chứa chữ số.")
            return value
        return ""
    
    @validates("email")
    def emailValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="user",
                    fieldName="email",
                    rule="Email chỉ được chứa tối đa 255 ký tự")
            if value.isspace():
                raise DataValidationError(
                    modelName="user",
                    fieldName="email",
                    rule="Email không hợp lệ")
            atCharacterIndex = value.find("@")
            if atCharacterIndex > 0:
                dotCharacterIndex = value.find(".", atCharacterIndex)
                if dotCharacterIndex - atCharacterIndex <= 1:
                    raise DataValidationError(
                        modelName="user",
                        fieldName="email",
                        rule="Email không hợp lệ.")
                return value
            raise DataValidationError(
                modelName="user",
                fieldName="email",
                rule="Email không hợp lệ")
        return ""
    
    @validates("idCardNumber")
    def idCardNumberValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 12:
                raise DataValidationError(
                    modelName="user",
                    fieldName="idCardNumber",
                    rule="Số căn cước chỉ được chứa tối đa 12 ký tự.")
            if not value.isalnum():
                raise DataValidationError(
                    modelName="user",
                    fieldName="idCardNumber",
                    rule="Số căn cước chỉ được chứa chữ và số.")
            return value
        return ""

    @validates("status")
    def statusValidating(self, _key: str, value: str | Statuses) -> str:
        if isinstance(value, self.Statuses):
            if value not in [value.value for value in self.Statuses]:
                raise ValueError(f"Value {value} for status is not valid")
            return value.value
        return value
    
    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="user",
                    fieldName="note",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự.")
            return value
        return ""
    
    def verifyPassword(self, password:str) -> bool:
        return bcrypt.check_password_hash(
            password=password,
            pw_hash=self.passwordHash)

    @hybrid_property
    def profilePicture(self) -> "Photo" | None:
        return next((photo for photo in self.photos if photo is not None), None)
    
    @hybrid_property
    def secondaryPhotos(self) -> List["Photo"]:
        return [photo for photo in self.photos if not photo.isPrimary]
    
    @hybrid_property
    def fullName(self) -> str:
        return " ".join([name for name in (self.firstName, self.middleName, self.lastName) if name])

    @fullName.expression
    def fullName(self) -> str:
        return func.concat_ws(
            " ",
            func.nullif(self.firstName, ""),
            func.nullif(self.middleName, ""),
            func.nullif(self.lastName, ""))
    
    @hybrid_property
    def isOnline(self) -> bool:
        if self.session is not None:
            lastAccessDateTime = Time.addTimeZoneToDateTime(self.session.lastAccessDateTime)
            deltaTime = Time.getCurrentDateTime() - lastAccessDateTime
            if deltaTime < timedelta(minutes=10):
                return True
        return False
    
    @hybrid_property
    def onlineStatus(self) -> str:
        if self.isOnline:
            return "Online"
        if self.session is not None:
            return Time.getTimeDeltaText(
                Time.getCurrentDateTime(),
                Time.addTimeZoneToDateTime(self.session.lastAccessDateTime)
            ) + " trước"
        return "Offline"
    
    @hybrid_property
    def birthdayString(self) -> str:
        if self.birthday is not None:
            return self.birthday.strftime("%d-%m-%Y")
        return ""
    
    @hybrid_property
    def joiningDateString(self) -> str:
        if self.joiningDate is not None:
            return self.joiningDate.strftime("%d-%m-%Y")
        return ""
    
    @hybrid_property
    def createdDateTimeString(self) -> str:
        if self.createdDateTime is not None:
            return self.createdDateTime.strftime("%d-%m-%Y %H:%M")
        return ""
    
    @hybrid_property
    def updatedDateTimeString(self) -> str:
        if self.updatedDateTime is not None:
            return self.updatedDateTime.strftime("%d-%m-%Y %H:%M")
        return ""
    
    @hybrid_property
    def updatedTimeDeltaString(self) -> str:
        return Time.getTimeDeltaText(
            Time.getCurrentDateTime(),
            Time.addTimeZoneToDateTime(self.updatedDateTime)
        ) + " trước"

def adjustingUpdatedDateTime(session: Session, _context: str, _instance: Callable[..., None]):
    for obj in session.dirty:
        if isinstance(obj, User):
            user = obj
            user.updatedDateTime = Time.getCurrentDateTime()
event.listens_for(Session, "before_flush", adjustingUpdatedDateTime)