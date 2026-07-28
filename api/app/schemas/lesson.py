"""Lesson Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExerciseRef(BaseModel):
    """Minimal exercise reference for lesson listings."""
    id: int
    slug: str
    title: str
    order: int


class LessonSummary(BaseModel):
    id: int
    slug: str
    title: str
    path: str = "core"
    order: int
    exercise_count: int
    exercises: list[ExerciseRef] = []


class LessonListResponse(BaseModel):
    lessons: list[LessonSummary]


class PathGroup(BaseModel):
    path: str
    display_name: str
    description: str
    color: str
    lessons: list[LessonSummary] = []


class LessonsByPathResponse(BaseModel):
    paths: list[PathGroup]


class ExerciseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    instruction: str
    starter_code: str
    order: int
    has_test_suite: bool = False


class LessonDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    content: str
    order: int
    exercises: list[ExerciseSummary]
