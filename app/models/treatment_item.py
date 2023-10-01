from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data import Base
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.treatment_session import TreatmentSession

class TreatmentItem(Base):
    # Table Name
    __tablename__ = "treatment_item"

    # Model Attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    sessionID: Mapped[int] = mapped_column(
        "session_id",
        Integer,
        ForeignKey("treatment_session.id", ondelete="CASCADE", onupdate="CASCADE"))
    productID: Mapped[int] = mapped_column(
        "product_id",
        Integer,
        ForeignKey("product.id", ondelete="CASCADE", onupdate="CASCADE"))
    price: Mapped[int] = mapped_column("price", Integer)
    vatFactor: Mapped[float] = mapped_column("vat_factor", Numeric)
    quatity: Mapped[int] = mapped_column("quatity", Integer)

    # Relationship
    session: Mapped["TreatmentSession"] = relationship("TreatmentSession", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="treatmentItems")