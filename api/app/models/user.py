"""User ORM model.

Tokens are now managed via JWT (stateless) — no token column on the User model.
"""

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")