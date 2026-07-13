"""Async SQLAlchemy engine and session management for SQLite."""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


# Allow override via environment variable
database_url = os.environ.get("DATABASE_URL", DATABASE_URL)

if database_url.startswith("sqlite"):
    # SQLite needs check_same_thread=False for aiosqlite
    engine = create_async_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_async_engine(database_url, echo=False)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """FastAPI dependency: yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables():
    """Create all tables. Safe to call on every startup — SQLAlchemy uses IF NOT EXISTS."""
    async with engine.begin() as conn:
        # Import models so they register with Base.metadata
        import app.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
