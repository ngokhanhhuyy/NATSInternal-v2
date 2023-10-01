from __future__ import annotations
from sqlalchemy import *
from app.data import Base

treatmentTherapist = Table(
    "treatment_therapist",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True),
    Column(
        "treatment_session_id",
        Integer,
        ForeignKey("treatment_session.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True))
