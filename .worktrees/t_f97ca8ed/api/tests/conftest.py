"""pytest configuration for FastAPI backend tests.

Uses an in-memory SQLite database, auto-creates tables, and provides
an async HTTP client via httpx.AsyncClient.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import create_app

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

test_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the FastAPI dependency with the test database session."""
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client against the test app."""
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a raw DB session for seeding test data."""
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register a test user and return Authorization headers."""
    resp = await client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert resp.status_code == 201
    token = resp.json()["token"]
    return {"Authorization": f"Bearer {token}"}