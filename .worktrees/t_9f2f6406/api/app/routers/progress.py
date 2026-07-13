"""Progress router: get user progress."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.progress import LessonProgressResponse, ProgressResponse
from app.services.progress import get_lesson_progress, get_user_progress

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("", response_model=ProgressResponse)
async def list_progress(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, summary = await get_user_progress(db, user)
    return ProgressResponse(progress=items, summary=summary)


@router.get("/{lesson_slug}", response_model=LessonProgressResponse)
async def lesson_progress(
    lesson_slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await get_lesson_progress(db, user, lesson_slug)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return LessonProgressResponse(**result)
