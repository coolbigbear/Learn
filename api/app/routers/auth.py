"""Auth router: register, login, logout, profile.

JWT-based authentication — tokens are stateless and self-validating.
No token column on the User model; logout is a client-side action.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import AuthRequest, AuthResponse, LogoutResponse, UserResponse
from app.services.auth import hash_password, verify_password
from app.services.jwt import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: AuthRequest, db: AsyncSession = Depends(get_db)):
    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token(user.id)
    return AuthResponse(id=user.id, username=user.username, token=token)


@router.post("/login", response_model=AuthResponse)
async def login(body: AuthRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.id)
    return AuthResponse(id=user.id, username=user.username, token=token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    user: User = Depends(get_current_user),
):
    """Logout is a client-side action — just acknowledge the request.

    The client discards the JWT token; the server has nothing to invalidate
    since JWT tokens are stateless.
    """
    return LogoutResponse(detail="Logged out")


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
):
    """Get the currently authenticated user's profile."""
    return UserResponse(id=user.id, username=user.username, created_at=user.created_at)