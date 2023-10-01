from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.data import Base
from app.models.treatment_therapist import treatmentTherapist
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.treatment import Treatment
    from app.models.treatment_item import TreatmentItem

class TreatmentSession(Base):
    # Table name
    __tablename__ = "treatment_session"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    treatmentID: Mapped[int] = mapped_column(
        "treatment_id",
        Integer,
        ForeignKey("treatment.id", ondelete="CASCADE", onupdate="CASCADE"))
    startingDateTime: Mapped[datetime] = mapped_column("starting_datetime", DateTime)
    endingDateTime: Mapped[datetime] = mapped_column("ending_datetime", DateTime)

    # Relationship
    treatment: Mapped["Treatment"] = relationship("Treatment", back_populates="sessions")
    items: Mapped[List["TreatmentItem"]] = relationship("TreatmentItem", back_populates="session")
    therapists: Mapped[List["User"]] = relationship(secondary=treatmentTherapist, back_populates="treatmentSessions")