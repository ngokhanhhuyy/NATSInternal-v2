from __future__ import annotations
from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.orm import validates, relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from app.data import getDatabaseSession, Session, Base
from app.errors import DataValidationError
from app.extensions.date_time import Time
from app.enum import Sexes
from datetime import date, datetime
from typing import List, Self, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.photo import Photo
    from app.models.order import Order
    from app.models.treatment import Treatment

class Customer(Base):
    # Table name
    __tablename__ = "customer"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str] = mapped_column("first_name", String(10))
    middleName: Mapped[str] = mapped_column("middle_name", String(20))
    lastName: Mapped[str] = mapped_column("last_name", String(10))
    nickName: Mapped[str] = mapped_column("nickname", String(35))
    company: Mapped[str] = mapped_column("company", String(50))
    sex: Mapped[str] = mapped_column("sex", Enum(Sexes, name="customerSexes"), default=Sexes.Undefined.value)
    birthday: Mapped[date | None] = mapped_column("birthday", Date)
    phone: Mapped[str] = mapped_column("phone", String(15))
    zalo: Mapped[str] = mapped_column("zalo", String(15))
    facebookURL: Mapped[str] = mapped_column("facebook_url", Text)
    email: Mapped[str] = mapped_column("email", String(255))
    address: Mapped[str] = mapped_column("address", String(255))
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime)
    updatedDateTime: Mapped[datetime] = mapped_column("updated_datetime", DateTime)
    introducedByID: Mapped[int | None] = mapped_column(
        "introduced_by_id",
        Integer,
        ForeignKey("customer.id", ondelete="SET NULL", onupdate="CASCADE"))
    note: Mapped[str] = mapped_column("note", String(255))

    # Relationship
    introducer: Mapped[Self] = relationship("Customer", remote_side=[id])
    photos: Mapped[List["Photo"]] = relationship("Photo", back_populates="customer")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    treatments: Mapped[List["Treatment"]] = relationship("Treatment", back_populates="customer")

    def __init__(self):
        super().__init__()
        self.createdDateTime = Time.getCurrentDateTime()
        self.updatedDateTime = Time.getCurrentDateTime()
    
    @validates("firstName")
    def firstNameValidating(self, _key: str, value: str) -> str:
        if len(value) != 0 and not value.isspace():
            if len(value) > 10:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="firstName",
                    rule="Họ chỉ được chứa tối đa 10 ký tự.")
            return value
        return ""
    
    @validates("middleName")
    def middleNameValidating(self, _key: str, value: str) -> str:
        if len(value) != 0 and not value.isspace():
            if len(value) > 20:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="middleName",
                    rule="Tên lót chỉ được chứa tối đa 20 ký tự.")
            return value
        return ""
    
    @validates("lastName")
    def lastNameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="customer",
                fieldName="lastName",
                rule="Tên không được để trống.")
        if len(value) > 35:
            raise DataValidationError(
                modelName="customer",
                fieldName="lastName",
                rule="Tên chỉ được chứa tối đa 10 ký tự.")
        return value
    
    @validates("nickName")
    def nickNameValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 35:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="nickName",
                    rule="Biệt danh chỉ được chứa tối đa 35 ký tự.")
            return value
        return ""
    
    @validates("company")
    def companyValidation(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 50:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="company",
                    rule="Tên công ty chỉ được chứa tối đa 50 ký tự.")
            return value
        return ""

    @validates("phone")
    def phoneValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 15:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="phone",
                    rule="Số điện thoại chỉ được chứa tối đa 15 ký tự.")
            if not value.isdigit():
                raise DataValidationError(
                    modelName="customer",
                    fieldName="phone",
                    rule="Số điện thoại chỉ được chứa chữ số.")
            return value
        return ""

    @validates("zalo")
    def phoneValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 15:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="zalo",
                    rule="Zalo chỉ được chứa tối đa 15 ký tự.")
            if not value.isdigit():
                raise DataValidationError(
                    modelName="customer",
                    fieldName="zalo",
                    rule="Zalo chỉ được chứa chữ số.")
            return value
        return ""
    
    @validates("facebookURL")
    def facebookURLValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if "https://facebook.com/" not in value:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="facebookURL",
                    rule="Địa chỉ facebook phải chứa tên miền 'https://facebook.com/'.")
            return value
        return ""
    
    @validates("email")
    def emailValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="email",
                    rule="Email chỉ được chứa tối đa 255 ký tự")
            if value.isspace():
                raise DataValidationError(
                    modelName="customer",
                    fieldName="email",
                    rule="Email không hợp lệ")
            atCharacterIndex = value.find("@")
            if atCharacterIndex > 0:
                dotCharacterIndex = value.find(".", atCharacterIndex)
                if dotCharacterIndex - atCharacterIndex <= 1:
                    raise DataValidationError(
                        modelName="customer",
                        fieldName="email",
                        rule="Email không hợp lệ.")
                return value
            raise DataValidationError(
                modelName="customer",
                fieldName="email",
                rule="Email không hợp lệ")
        return ""
    
    @validates("address")
    def addressValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="address",
                    rule="Địa chỉ chỉ được chứa tối đa 255 ký tự")
            return value
        return ""
    
    @validates("note")
    def noteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="customer",
                    fieldName="note",
                    rule="Ghi chú chỉ được chứa tối đa 255 ký tự")
            return value
        return ""
    
    @hybrid_property
    def profilePicture(self) -> "Photo" | None:
        return next((photo for photo in self.photos if photo.isPrimary), None)
    
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
            self.lastName)

def adjustingUpdatedDateTime(session: Session, _context: str, _instance: Callable[..., None]):
    for obj in session.dirty:
        if isinstance(obj, Customer):
            customer = obj
            customer.updatedDateTime = Time.getCurrentDateTime()
event.listen(Session, "before_flush", adjustingUpdatedDateTime)