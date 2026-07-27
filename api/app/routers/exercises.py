"""Exercises router: run, submit, and view exercise details."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.exercise import CodeSubmission, ExerciseDetail, RunResult
from app.services.exercise_runner import run_code, run_code_with_docker_fallback
from app.services.lesson import get_exercise_by_id
from app.services.progress import get_or_create_progress

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.get("/{exercise_id}", response_model=ExerciseDetail)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get exercise details (instruction, starter_code, etc.) without test cases or solution."""
    exercise = await get_exercise_by_id(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    return ExerciseDetail(
        id=exercise.id,
        slug=exercise.slug,
        title=exercise.title,
        instruction=exercise.instruction,
        starter_code=exercise.starter_code,
        language=exercise.language,
        order=exercise.order,
        lesson_id=exercise.lesson_id,
        has_test_suite=bool(exercise.test_suite),
    )


@router.post("/{exercise_id}/run", response_model=RunResult)
async def run_exercise(
    exercise_id: int,
    body: CodeSubmission,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    exercise = await get_exercise_by_id(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    test_cases = [] if exercise.test_suite else (exercise.test_cases or [])
    result = await run_code_with_docker_fallback(
        body.code,
        test_cases,
        language=body.language,
        test_suite=exercise.test_suite,
    )
    return RunResult(**result)


@router.post("/{exercise_id}/submit", response_model=RunResult)
async def submit_exercise(
    exercise_id: int,
    body: CodeSubmission,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    exercise = await get_exercise_by_id(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    test_cases = [] if exercise.test_suite else (exercise.test_cases or [])
    result = await run_code_with_docker_fallback(
        body.code,
        test_cases,
        language=body.language,
        test_suite=exercise.test_suite,
    )

    progress = await get_or_create_progress(db, user, exercise_id)
    if progress is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    if result["passed"]:
        progress.mark_completed(body.code)
    else:
        progress.increment_attempts()
        progress.code_submitted = body.code

    await db.flush()
    return RunResult(**result)
