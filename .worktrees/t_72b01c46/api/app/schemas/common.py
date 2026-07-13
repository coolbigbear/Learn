"""Reusable API schemas for common patterns."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response body."""
    detail: str
    error_code: str | None = None