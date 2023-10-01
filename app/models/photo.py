from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from app.data import Base
from enum import IntEnum
from typing import List, TYPE_CHECKING
from base64 import b64encode
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.brand import Brand
    from app.models.product import Product

class Photo(Base):
    # Table name
    __tablename__ = "photo"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    content: Mapped[bytes] = mapped_column("content", LargeBinary)
    isPrimary: Mapped[bool] = mapped_column("is_primary", Boolean)
    userID: Mapped[int | None] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    customerID: Mapped[int | None] = mapped_column(
        "customer_id",
        Integer,
        ForeignKey("customer.id", ondelete="CASCADE", onupdate="CASCADE"))
    brandID: Mapped[int | None] = mapped_column(
        "brand_id",
        Integer,
        ForeignKey("brand.id", ondelete="CASCADE", onupdate="CASCADE"))
    productID: Mapped[int | None] = mapped_column(
        "product_id",
        Integer,
        ForeignKey("product.id", ondelete="CASCADE", onupdate="CASCADE"))
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="photos")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="photos")
    brand: Mapped["Brand"] = relationship("Brand", back_populates="photos")
    product: Mapped["Product"] = relationship("Product", back_populates="photos")

    @hybrid_property
    def contentDecoded(self) -> str | None:
        if self.content is not None:
            return b64encode(self.content).decode("utf-8")
        return None