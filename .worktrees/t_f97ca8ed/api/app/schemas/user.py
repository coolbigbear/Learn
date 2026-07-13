"""User Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=80)
    password: str = Field(..., min_length=4, max_length=128)


class AuthResponse(BaseModel):
    id: int
    username: str
    token: str


class LogoutResponse(BaseModel):
    detail: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime | None = None
