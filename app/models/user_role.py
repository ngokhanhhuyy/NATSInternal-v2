from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from app.data import Base
    
userRole = Table(
    "user_role",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True),
    Column(
        "role_id",
        Integer,
        ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True))