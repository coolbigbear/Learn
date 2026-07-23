"""Admin router: maintenance endpoints for content re-seeding and system health."""

import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.content_seed import seed_content

# Users allowed to access sensitive admin operations.
# Set via ADMIN_USERNAMES env var (comma-separated) or default to the
# auto-seeded developer profile.
_ADMIN_USERNAMES_ENV = os.environ.get("ADMIN_USERNAMES", "")
if _ADMIN_USERNAMES_ENV:
    ADMIN_USERNAMES = {name.strip() for name in _ADMIN_USERNAMES_ENV.split(",")}
else:
    ADMIN_USERNAMES = {"admin", "developer"}

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin(user: User) -> None:
    """Raise 403 if the user is not in the admin usernames set."""
    if user.username not in ADMIN_USERNAMES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this operation",
        )


@router.post("/re-seed")
async def re_seed(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Flush all existing lesson content and re-import from the manifest.

    Deletes all existing lessons (and their exercises via explicit cascade)
    and re-imports everything from the content directory manifest.

    Restricted to administrator users only.
    """
    _require_admin(user)
    result = await seed_content(session=db, reimport=True)
    return result
