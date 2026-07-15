"""Tests for progress endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.models.lesson import Lesson
from app.models.progress import UserProgress
from app.models.user import User
from app.services.jwt import create_access_token


@pytest.fixture(autouse=True)
async def seed_progress_data(db_session: AsyncSession):
    """Seed a lesson with exercises and a user's progress."""
    lesson = Lesson(
        slug="10-progress-test",
        title="Progress Test Lesson",
        content="# Progress",
        order=10,
    )
    db_session.add(lesson)
    await db_session.flush()

    ex1 = Exercise(
        lesson_id=lesson.id,
        slug="prog-ex-1",
        title="Progress Ex 1",
        instruction="Do it",
        starter_code="# code",
        solution_code='print("ok")',
        test_cases=[{"input": "", "expected_output": "ok\n", "comparison_type": "exact"}],
        order=1,
    )
    ex2 = Exercise(
        lesson_id=lesson.id,
        slug="prog-ex-2",
        title="Progress Ex 2",
        instruction="Do it too",
        starter_code="# code",
        solution_code='print("ok2")',
        test_cases=[{"input": "", "expected_output": "ok2\n", "comparison_type": "exact"}],
        order=2,
    )
    db_session.add_all([ex1, ex2])
    await db_session.flush()

    # Create a test user with progress on ex1
    user = User(username="progress_user", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    # Generate a JWT token for the test user (stateless — no token column)
    token = create_access_token(user.id)

    up = UserProgress(
        user_id=user.id,
        exercise_id=ex1.id,
        completed=True,
        code_submitted='print("ok")',
        attempts=2,
    )
    db_session.add(up)
    await db_session.flush()

    # Store for tests
    pytest.progress_headers = {"Authorization": f"Bearer {token}"}
    pytest.progress_ex1_id = ex1.id
    pytest.progress_ex2_id = ex2.id
    pytest.progress_lesson_slug = "10-progress-test"
    yield


class TestListProgress:
    async def test_progress_all(self, client: AsyncClient):
        resp = await client.get("/api/progress", headers=pytest.progress_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "progress" in body
        assert "summary" in body
        assert "lesson_totals" in body
        # Should have progress for ex1
        exercise_ids = [p["exercise_id"] for p in body["progress"]]
        assert pytest.progress_ex1_id in exercise_ids
        # Lesson totals should include test lesson with 2 exercises
        lesson_slug = pytest.progress_lesson_slug
        assert lesson_slug in body["lesson_totals"]
        assert body["lesson_totals"][lesson_slug] >= 2
        # Summary
        assert body["summary"]["total_exercises"] >= 2
        assert body["summary"]["completed_exercises"] >= 1

    async def test_progress_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/progress")
        assert resp.status_code == 401


class TestLessonProgress:
    async def test_lesson_progress_success(self, client: AsyncClient):
        resp = await client.get(
            f"/api/progress/{pytest.progress_lesson_slug}",
            headers=pytest.progress_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["lesson_slug"] == pytest.progress_lesson_slug
        assert len(body["exercises"]) >= 1

    async def test_lesson_progress_not_found(self, client: AsyncClient):
        resp = await client.get(
            "/api/progress/nonexistent-lesson",
            headers=pytest.progress_headers,
        )
        assert resp.status_code == 404

    async def test_lesson_progress_requires_auth(self, client: AsyncClient):
        resp = await client.get(f"/api/progress/{pytest.progress_lesson_slug}")
        assert resp.status_code == 401
