from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.data import Base
from app.extensions.date_time import Time
from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING
import secrets
if TYPE_CHECKING:
    from app.models.user import User

class UserSession(Base):
    # Table name
    __tablename__ = "user_session"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True)
    token: Mapped[str] = mapped_column("token", String(24))
    loggedInDateTime: Mapped[datetime] = mapped_column("logged_in_datetime", DateTime)
    expiringDateTime: Mapped[datetime] = mapped_column("expiring_datetime", DateTime)
    lastAccessDateTime: Mapped[datetime] = mapped_column("last_access_datetime", DateTime)
    ipAddress: Mapped[str] = mapped_column("ip_address", String(15))
    userAgent: Mapped[str] = mapped_column("user_agent", String)

    # Relationship
    user: Mapped["User"] = relationship("User", uselist=False, back_populates="session")

    def __init__(self, userID: int, ipAddress: str = None, userAgent: str = None):
        super().__init__()
        self.userID = userID
        self.generateNewSessionToken(
            ipAddress=ipAddress,
            userAgent=userAgent)

    def generateNewSessionToken(self, ipAddress: str, userAgent: str):
        self.token = secrets.token_hex(12)
        self.loggedInDateTime = Time.getCurrentDateTime()
        self.expiringDateTime = Time.getCurrentDateTime() + timedelta(hours=1)
        self.lastAccessDateTime = Time.getCurrentDateTime()
        self.ipAddress = ipAddress
        self.userAgent = userAgent

    def refreshSession(self):
        self.expiringDateTime = Time.getCurrentDateTime() + timedelta(hours=1)
        self.lastAccessDateTime = Time.getCurrentDateTime()