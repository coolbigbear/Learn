"""Lesson service: query helpers."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exercise import Exercise
from app.models.lesson import Lesson


async def get_lessons_with_counts(db: AsyncSession) -> list[dict]:
    """Return all lessons ordered, with exercise counts."""
    stmt = (
        select(
            Lesson.id,
            Lesson.slug,
            Lesson.title,
            Lesson.order,
            func.count(Exercise.id).label("exercise_count"),
        )
        .outerjoin(Exercise, Exercise.lesson_id == Lesson.id)
        .group_by(Lesson.id)
        .order_by(Lesson.order)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [
        {
            "id": row.id,
            "slug": row.slug,
            "title": row.title,
            "order": row.order,
            "exercise_count": row.exercise_count,
        }
        for row in rows
    ]


async def get_lesson_by_slug(db: AsyncSession, slug: str) -> Lesson | None:
    result = await db.execute(
        select(Lesson).options(selectinload(Lesson.exercises)).where(Lesson.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_exercise_by_id(db: AsyncSession, exercise_id: int) -> Exercise | None:
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    return result.scalar_one_or_none()