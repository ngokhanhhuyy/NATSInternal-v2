from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from app.extensions.date_time import Time
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.supply import Supply
    from app.models.product import Product
    from app.models.order_item import OrderItem

class SupplyItem(Base):
    # Table name
    __tablename__ = "supply_item"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    supplyID: Mapped[int] = mapped_column(
        "supply_id",
        Integer,
        ForeignKey("supply.id", ondelete="CASCADE", onupdate="CASCADE"))
    productID: Mapped[int] = mapped_column(
        "product_id",
        Integer,
        ForeignKey("product.id", ondelete="CASCADE", onupdate="CASCADE"))
    price: Mapped[int] = mapped_column("price", Integer)
    vatFactor: Mapped[float] = mapped_column("vat_factor", Numeric, default=0.1)
    suppliedQuatity: Mapped[int] = mapped_column("supplied_quatity", Integer, default=1)
    stockQuatity: Mapped[int] = mapped_column("stock_quatity", Integer)

    # Relationship
    supply: Mapped["Supply"] = relationship("Supply", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="supplyItems")
    orderItems: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="supplyItem")

