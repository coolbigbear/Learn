"""Lesson Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LessonSummary(BaseModel):
    id: int
    slug: str
    title: str
    order: int
    exercise_count: int


class LessonListResponse(BaseModel):
    lessons: list[LessonSummary]


class ExerciseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    instruction: str
    starter_code: str
    order: int


class LessonDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    content: str
    order: int
    exercises: list[ExerciseSummary]
