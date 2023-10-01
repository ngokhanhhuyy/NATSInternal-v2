from __future__ import annotations
from sqlalchemy import *
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from app.data import Base
from app.extensions.date_time import Time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import secrets
if TYPE_CHECKING:
    from app.models.user import User

# noinspection PyTypeChecker
class UserApiKey(Base):
    # Table name
    __tablename__ = "user_api_key"

    # Model attributes
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    userID: Mapped[int] = mapped_column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True)
    key: Mapped[str] = mapped_column("key", String(64))
    createdDateTime: Mapped[datetime] = mapped_column("created_datetime", DateTime)
    lastUsedDateTime: Mapped[datetime | None] = mapped_column("last_used_datetime", DateTime)
    lastUsedIPAddress: Mapped[str] = mapped_column("last_used_ip_address", String(15), default="")

    # Relationship
    user: Mapped["User"] = relationship("User", uselist=False, back_populates="apiKey")

    def __init__(self, userID: int):
        super().__init__()
        self.userID = userID
        self.key = secrets.token_hex(32)
        self.createdDateTime = Time.getCurrentDateTime()