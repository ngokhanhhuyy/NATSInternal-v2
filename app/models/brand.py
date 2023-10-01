from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship, Mapped, mapped_column
from app.data import Base
from app.errors import DataValidationError
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.photo import Photo
    from app.models.country import Country

class Brand(Base):
    # Table name
    __tablename__ = "brand"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("name", String(50), unique=True)
    countryID: Mapped[int | None] = mapped_column(
        "country_id",
        Integer,
        ForeignKey("country.id", ondelete="SET NULL", onupdate="CASCADE"))
    website: Mapped[str] = mapped_column("website", String)
    socialMediaURL: Mapped[str] = mapped_column("social_media_url", String)
    phone: Mapped[str] = mapped_column("phone", String(15))
    email: Mapped[str] = mapped_column("email", String(255))
    address: Mapped[str] = mapped_column("address", String)

    # Relationship
    photos: Mapped["Photo"] = relationship("Photo", uselist=True, back_populates="brand")
    products: Mapped[List["Product"]] = relationship("Product", uselist=True, back_populates="brand")
    country: Mapped["Country"] = relationship("Country", uselist=False, back_populates="brands")
    
    @validates("name")
    def nameValidating(self, _key: str, value: str) -> str:
        if len(value) == 0 or value.isspace():
            raise DataValidationError(
                modelName="brand",
                fieldName="name",
                rule="Tên thương hiệu không được để trống.")
        if len(value) > 50:
            raise DataValidationError(
                modelName="brand",
                fieldName="name",
                rule="Tên thương hiệu chỉ được chứa tối đa 50 ký tự.")
        return value
    
    @validates("website")
    def websiteValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if "http://" not in value and "https://" not in value:
                return "http://" + value
            return value
        return ""
    
    @validates("socialMediaURL")
    def socialMediaURLValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if "http://" not in value and "https://" not in value:
                return "http://" + value
            return value
        return ""
    
    @validates("phone")
    def phoneValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 15:
                raise DataValidationError(
                    modelName="brand",
                    fieldName="phone",
                    rule="Số điện thoại chỉ được chứa tối đa 15 chữ số")
            if not value.isdigit():
                raise DataValidationError(
                    modelName="brand",
                    fieldName="name",
                    rule="Tên thương hiệu chỉ được chứa chữ số.")
            return value
        return ""
    
    @validates("email")
    def emailValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            if len(value) > 255:
                raise DataValidationError(
                    modelName="brand",
                    fieldName="email",
                    rule="Email chỉ được chứa tối đa 255 ký tự")
            if value.isspace():
                raise DataValidationError(
                    modelName="brand",
                    fieldName="email",
                    rule="Email không hợp lệ")
            atCharacterIndex = value.find("@")
            if atCharacterIndex > 0:
                dotCharacterIndex = value.find(".", atCharacterIndex)
                if dotCharacterIndex - atCharacterIndex <= 1:
                    raise DataValidationError(
                        modelName="brand",
                        fieldName="email",
                        rule="Email không hợp lệ.")
                return value
            raise DataValidationError(
                modelName="brand",
                fieldName="email",
                rule="Email không hợp lệ")
        return ""
    
    @validates("address")
    def addressValidating(self, _key: str, value: str) -> str:
        if len(value) > 0 and not value.isspace():
            return value
        return ""