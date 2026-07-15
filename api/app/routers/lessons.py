"""Lessons router: list lessons, get lesson detail."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.lesson import (
    LessonDetail,
    LessonListResponse,
    LessonsByPathResponse,
    PathGroup,
)
from app.services.lesson import (
    get_lesson_by_slug,
    get_lessons_grouped_by_path,
    get_lessons_with_counts,
)


router = APIRouter(prefix="/api/lessons", tags=["lessons"])


@router.get("", response_model=LessonListResponse)
async def list_lessons(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lessons = await get_lessons_with_counts(db)
    return LessonListResponse(lessons=lessons)


# Path display metadata
PATH_META = {
    "core": {
        "display_name": "Python Fundamentals",
        "description": "Master the core building blocks of Python — variables, data types, functions, and object-oriented programming.",
        "color": "indigo",
    },
    "data-processing": {
        "display_name": "Data Processing",
        "description": "Learn to work with real-world data — CSV files, JSON, and APIs using Python.",
        "color": "green",
    },
    "api": {
        "display_name": "API Development",
        "description": "Build web APIs with FastAPI, from routes to a complete mini project.",
        "color": "blue",
    },
    "machine-learning": {
        "display_name": "Machine Learning",
        "description": "Explore ML concepts, model training, and deployment. Coming soon!",
        "color": "purple",
    },
}


@router.get("/by-path", response_model=LessonsByPathResponse)
async def list_lessons_by_path(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return lessons grouped by learning path with path metadata."""
    grouped = await get_lessons_grouped_by_path(db)

    paths = []
    # Ensure a consistent order: core first, then data-processing, api, machine-learning
    for path_key in ["core", "data-processing", "api", "machine-learning"]:
        meta = PATH_META.get(path_key, {"display_name": path_key, "description": "", "color": "gray"})
        lessons = grouped.get(path_key, [])
        paths.append(
            PathGroup(
                path=path_key,
                display_name=meta["display_name"],
                description=meta["description"],
                color=meta["color"],
                lessons=lessons,
            )
        )

    return LessonsByPathResponse(paths=paths)


@router.get("/{slug}", response_model=LessonDetail)
async def get_lesson(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lesson = await get_lesson_by_slug(db, slug)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    exercises = []
    for ex in lesson.exercises:
        exercises.append({
            "id": ex.id,
            "slug": ex.slug,
            "title": ex.title,
            "instruction": ex.instruction,
            "starter_code": ex.starter_code,
            "order": ex.order,
        })

    return LessonDetail(
        id=lesson.id,
        slug=lesson.slug,
        title=lesson.title,
        content=lesson.content,
        order=lesson.order,
        exercises=exercises,
    )
