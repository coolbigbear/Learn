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
            Lesson.path,
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
            "path": row.path,
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


async def get_lessons_grouped_by_path(db: AsyncSession) -> dict[str, list[dict]]:
    """Return lessons grouped by their learning path."""
    stmt = (
        select(
            Lesson.id,
            Lesson.slug,
            Lesson.title,
            Lesson.order,
            Lesson.path,
            func.count(Exercise.id).label("exercise_count"),
        )
        .outerjoin(Exercise, Exercise.lesson_id == Lesson.id)
        .group_by(Lesson.id)
        .order_by(Lesson.order)
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Known paths in display order
    known_paths = ["core", "data-processing", "api", "machine-learning"]

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        lesson_dict = {
            "id": row.id,
            "slug": row.slug,
            "title": row.title,
            "order": row.order,
            "path": row.path,
            "exercise_count": row.exercise_count,
        }
        grouped.setdefault(row.path, []).append(lesson_dict)

    # Ensure all known paths are present, even if empty
    for p in known_paths:
        grouped.setdefault(p, [])

    return grouped