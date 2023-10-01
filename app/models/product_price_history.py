from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, validates, Mapped, mapped_column
from app.data import Base
from app.extensions.date_time import Time
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.product import Product

class ProductPriceHistory(Base):
    # Table
    __tablename__ = "product_price_history"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    productID: Mapped[int] = mapped_column(
        "product_id",
        Integer,
        ForeignKey("product.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False)
    price: Mapped[int] = mapped_column("price", Integer)
    loggedDateTime: Mapped[datetime] = mapped_column("logged_datetime", DateTime)

    # Relationship
    product: Mapped["Product"] = relationship("Product", back_populates="prices")

    def __init__(self):
        self.loggedDateTime = Time.getCurrentDateTime()