"""Exercise ORM model."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    instruction = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=False, default="# Write your code here\n")
    solution_code = Column(Text, nullable=False, default="")
    test_cases = Column(JSON, nullable=False, default=list)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="exercises")
    progress = relationship("UserProgress", back_populates="exercise", cascade="all, delete-orphan")
