"""Lessons router: list lessons, get lesson detail."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.lesson import LessonDetail, LessonListResponse
from app.services.lesson import get_lesson_by_slug, get_lessons_with_counts

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


@router.get("", response_model=LessonListResponse)
async def list_lessons(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lessons = await get_lessons_with_counts(db)
    return LessonListResponse(lessons=lessons)


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
