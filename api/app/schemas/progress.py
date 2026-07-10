"""Progress Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class ProgressItem(BaseModel):
    exercise_id: int
    exercise_slug: str
    lesson_slug: str
    completed: bool
    attempts: int
    completed_at: datetime | None = None


class ProgressSummary(BaseModel):
    total_exercises: int
    completed_exercises: int
    percentage: float


class ProgressResponse(BaseModel):
    progress: list[ProgressItem]
    summary: ProgressSummary
    lesson_totals: dict[str, int]  # lesson_slug -> total_exercises


class LessonProgressItem(BaseModel):
    exercise_id: int
    exercise_slug: str
    completed: bool
    attempts: int
    completed_at: datetime | None = None


class LessonProgressResponse(BaseModel):
    lesson_slug: str
    exercises: list[LessonProgressItem]
