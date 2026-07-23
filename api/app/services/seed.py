"""Seed users for Hermes profiles on non-production startup.

Each Hermes profile (content, backend, frontend, reviewer, architect, user)
gets a corresponding DB user so they can authenticate without manual registration
during development and testing.

Skipped when PRODUCTION=1 is set.
"""

from sqlalchemy import select

from app.database import async_session_factory
from app.models.user import User
from app.services.auth import hash_password

# Default password for all dev profile users
DEFAULT_PASSWORD = "devprofile"

# Map of Hermes profile → database username
PROFILE_USERS = [
    "content",
    "backend",
    "frontend",
    "reviewer",
    "architect",
    "user",
    "testuser",
    "developer",
]


async def ensure_profile_users() -> list[User]:
    """Ensure a DB user exists for every Hermes profile.

    Returns the list of created users (empty if all already existed).
    Skips silently if the user already exists.
    """
    created: list[User] = []
    hashed = hash_password(DEFAULT_PASSWORD)

    async with async_session_factory() as session:
        async with session.begin():
            for username in PROFILE_USERS:
                result = await session.execute(
                    select(User).where(User.username == username)
                )
                if result.scalar_one_or_none() is not None:
                    continue  # already exists

                user = User(
                    username=username,
                    password_hash=hashed,
                )
                session.add(user)
                created.append(user)
        # session.begin() commits on block exit

    return created