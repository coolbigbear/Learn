"""User ORM model."""

import uuid

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    token = Column(String(64), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")

    def generate_token(self) -> str:
        """Generate a new UUID token (48 hex chars)."""
        self.token = uuid.uuid4().hex + uuid.uuid4().hex[:16]  # 48 chars
        return self.token

    def clear_token(self) -> None:
        self.token = None
