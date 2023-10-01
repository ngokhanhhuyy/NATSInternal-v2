from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from app.data import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product import Product
    from app.models.supply_item import SupplyItem

class OrderItem(Base):
    # Table name
    __tablename__ = "order_item"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    orderID: Mapped[int] = mapped_column(
        "order_id",
        Integer,
        ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"))
    productID: Mapped[int] = mapped_column(
        "product_id",
        Integer,
        ForeignKey("product.id", ondelete="CASCADE", onupdate="CASCADE"))
    supplyItemID: Mapped[int] = mapped_column(
        "supply_item_id",
        Integer,
        ForeignKey("supply_item.id", ondelete="CASCADE", onupdate="CASCADE"))
    price: Mapped[int] = mapped_column("price", Integer)
    vatFactor: Mapped[float] = mapped_column("vat_factor", Numeric, default=0.1)
    quatity: Mapped[int] = mapped_column("quatity", Integer, default=1)
    pinned: Mapped[bool] = mapped_column("pinned", Boolean, default=False)

    # Relationship
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="orderItems")
    supplyItem: Mapped["SupplyItem"] = relationship("SupplyItem", back_populates="orderItems")

