"""Progress service: query helpers."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.models.lesson import Lesson
from app.models.progress import UserProgress
from app.models.user import User


async def get_user_progress(db: AsyncSession, user: User) -> tuple[list[dict], dict, dict]:
    """Get full progress for a user across all exercises.

    Returns (progress_items, summary_dict, lesson_totals_dict).
    """
    # Total exercises count
    total_result = await db.execute(select(func.count(Exercise.id)))
    total_exercises = total_result.scalar() or 0

    # Per-lesson exercise totals
    lesson_totals_result = await db.execute(
        select(
            Lesson.slug,
            func.count(Exercise.id).label("total"),
        )
        .join(Exercise, Exercise.lesson_id == Lesson.id)
        .group_by(Lesson.slug)
    )
    lesson_totals = dict(lesson_totals_result.all())

    # User's progress
    stmt = (
        select(
            UserProgress,
            Exercise.slug.label("exercise_slug"),
            Lesson.slug.label("lesson_slug"),
        )
        .join(Exercise, Exercise.id == UserProgress.exercise_id)
        .join(Lesson, Lesson.id == Exercise.lesson_id)
        .where(UserProgress.user_id == user.id)
    )
    result = await db.execute(stmt)
    rows = result.all()

    progress_items = []
    for row in rows:
        up: UserProgress = row[0]
        progress_items.append({
            "exercise_id": up.exercise_id,
            "exercise_slug": row.exercise_slug,
            "lesson_slug": row.lesson_slug,
            "completed": up.completed,
            "attempts": up.attempts,
            "completed_at": up.completed_at,
        })

    completed_count = sum(1 for p in progress_items if p["completed"])
    percentage = round(completed_count / total_exercises * 100, 1) if total_exercises else 0.0

    summary = {
        "total_exercises": total_exercises,
        "completed_exercises": completed_count,
        "percentage": percentage,
    }

    return progress_items, summary, lesson_totals


async def get_lesson_progress(db: AsyncSession, user: User, lesson_slug: str) -> dict | None:
    """Get progress for exercises in a specific lesson."""
    lesson_result = await db.execute(select(Lesson).where(Lesson.slug == lesson_slug))
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        return None

    stmt = (
        select(
            UserProgress,
            Exercise.slug.label("exercise_slug"),
        )
        .join(Exercise, Exercise.id == UserProgress.exercise_id)
        .where(
            UserProgress.user_id == user.id,
            Exercise.lesson_id == lesson.id,
        )
    )
    result = await db.execute(stmt)
    rows = result.all()

    exercises = []
    for row in rows:
        up: UserProgress = row[0]
        exercises.append({
            "exercise_id": up.exercise_id,
            "exercise_slug": row.exercise_slug,
            "completed": up.completed,
            "attempts": up.attempts,
            "completed_at": up.completed_at,
        })

    return {
        "lesson_slug": lesson_slug,
        "exercises": exercises,
    }


async def get_or_create_progress(
    db: AsyncSession, user: User, exercise_id: int
) -> UserProgress | None:
    """Get existing progress or create a new one."""
    from sqlalchemy import select as sel

    result = await db.execute(
        sel(UserProgress).where(
            UserProgress.user_id == user.id,
            UserProgress.exercise_id == exercise_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        # Verify exercise exists
        ex_result = await db.execute(sel(Exercise).where(Exercise.id == exercise_id))
        if ex_result.scalar_one_or_none() is None:
            return None
        progress = UserProgress(
            user_id=user.id,
            exercise_id=exercise_id,
            completed=False,
            attempts=0,
        )
        db.add(progress)
        await db.flush()
    return progress