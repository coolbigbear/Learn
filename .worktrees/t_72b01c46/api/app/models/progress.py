"""UserProgress ORM model."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    completed = Column(Boolean, default=False)
    code_submitted = Column(Text, nullable=True)
    attempts = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "exercise_id", name="uq_user_exercise"),
    )

    user = relationship("User", back_populates="progress")
    exercise = relationship("Exercise", back_populates="progress")

    def mark_completed(self, code: str) -> None:
        self.completed = True
        self.code_submitted = code
        self.attempts += 1
        self.completed_at = datetime.now(timezone.utc)

    def increment_attempts(self) -> None:
        self.attempts += 1
