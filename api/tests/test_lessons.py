"""Tests for lesson endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.models.lesson import Lesson


@pytest.fixture(autouse=True)
async def seed_lessons(db_session: AsyncSession):
    """Seed test data: two lessons with exercises."""
    lesson1 = Lesson(
        slug="01-test-lesson",
        title="Test Lesson One",
        content="# Test\n\nContent here.",
        order=1,
    )
    lesson2 = Lesson(
        slug="02-test-lesson",
        title="Test Lesson Two",
        content="# Test Two\n\nMore content.",
        order=2,
    )
    db_session.add_all([lesson1, lesson2])
    await db_session.flush()

    ex1 = Exercise(
        lesson_id=lesson1.id,
        slug="test-ex-1",
        title="First Exercise",
        instruction="Write code",
        starter_code="# Write here\n",
        solution_code="print('ok')",
        test_cases=[{"input": "", "expected_output": "ok\n", "comparison_type": "exact"}],
        order=1,
    )
    ex2 = Exercise(
        lesson_id=lesson1.id,
        slug="test-ex-2",
        title="Second Exercise",
        instruction="Do something",
        starter_code="# Do it\n",
        solution_code="print('done')",
        test_cases=[{"input": "", "expected_output": "done\n", "comparison_type": "exact"}],
        order=2,
    )
    db_session.add_all([ex1, ex2])
    await db_session.flush()
    yield


class TestListLessons:
    async def test_list_lessons(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/lessons", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "lessons" in body
        assert len(body["lessons"]) == 2
        # First lesson should have exercise_count = 2
        assert body["lessons"][0]["exercise_count"] == 2
        assert body["lessons"][1]["exercise_count"] == 0
        # Should include path field
        assert body["lessons"][0]["path"] == "core"

    async def test_lessons_ordered(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/lessons", headers=auth_headers)
        lessons = resp.json()["lessons"]
        assert lessons[0]["slug"] == "01-test-lesson"
        assert lessons[1]["slug"] == "02-test-lesson"

    async def test_lessons_require_auth(self, client: AsyncClient):
        resp = await client.get("/api/lessons")
        assert resp.status_code == 401


class TestLessonsByPath:
    async def test_by_path_groups_lessons(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/lessons/by-path", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "paths" in body
        assert len(body["paths"]) == 4  # core, data-processing, api, machine-learning

        # core path should have 2 test lessons
        core_path = body["paths"][0]
        assert core_path["path"] == "core"
        assert core_path["display_name"] == "Python Fundamentals"
        assert len(core_path["lessons"]) == 2
        for lesson in core_path["lessons"]:
            assert lesson["path"] == "core"
            assert lesson["exercise_count"] is not None
            assert "exercises" in lesson
            # First lesson has 2 exercises, second has 0
            if lesson["slug"] == "01-test-lesson":
                assert lesson["exercise_count"] == 2
                assert len(lesson["exercises"]) == 2
                # Verify exercise fields
                ex1 = lesson["exercises"][0]
                assert "id" in ex1
                assert ex1["slug"] == "test-ex-1"
                assert ex1["title"] == "First Exercise"
                assert ex1["order"] == 1
                # Must not include sensitive/extra fields
                assert "instruction" not in ex1
                assert "starter_code" not in ex1
                ex2 = lesson["exercises"][1]
                assert ex2["slug"] == "test-ex-2"
                assert ex2["order"] == 2
            else:
                assert lesson["exercise_count"] == 0
                assert lesson["exercises"] == []

        # Other paths should be empty for now
        assert body["paths"][1]["path"] == "data-processing"
        assert body["paths"][1]["lessons"] == []
        assert body["paths"][2]["path"] == "api"
        assert body["paths"][2]["lessons"] == []
        assert body["paths"][3]["path"] == "machine-learning"
        assert body["paths"][3]["lessons"] == []

    async def test_by_path_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/lessons/by-path")
        assert resp.status_code == 401


class TestGetLesson:
    async def test_get_lesson_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/lessons/01-test-lesson", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["slug"] == "01-test-lesson"
        assert body["title"] == "Test Lesson One"
        assert "exercises" in body
        assert len(body["exercises"]) == 2

    async def test_get_lesson_returns_public_fields(self, client: AsyncClient, auth_headers: dict):
        """Ensure solution_code and test_cases are NOT returned."""
        resp = await client.get("/api/lessons/01-test-lesson", headers=auth_headers)
        ex = resp.json()["exercises"][0]
        assert "solution_code" not in ex
        assert "test_cases" not in ex
        assert "starter_code" in ex  # starter code IS public

    async def test_get_lesson_not_found(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/lessons/nonexistent", headers=auth_headers)
        assert resp.status_code == 404

    async def test_get_lesson_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/lessons/01-test-lesson")
        assert resp.status_code == 401
