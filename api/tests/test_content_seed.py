"""Tests for the content seed service.

Covers incremental seeding: new lessons should be added even when the
database already has existing lessons.
"""

import json
import os
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.models.lesson import Lesson

# Ensure we use the test database
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")


# The module we're testing
from app.services.content_seed import seed_content


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _lesson_dir(base: Path, path_key: str, slug: str) -> Path:
    """Return the lesson directory under a path-based content structure."""
    return base / path_key / slug


def _write_lesson(base: Path, lesson: dict) -> None:
    """Create lesson files (lesson.md + exercises.json) under the path-based dir."""
    pth = lesson.get("path", "python")
    slug = lesson["slug"]
    lesson_dir = _lesson_dir(base, pth, slug)
    lesson_dir.mkdir(parents=True)
    (lesson_dir / "lesson.md").write_text(
        f"# {lesson['title']}\n\nLesson content.\n", encoding="utf-8"
    )
    exercises = [
        {
            "slug": f"{slug}-ex1",
            "title": f"{lesson['title']} Exercise",
            "instruction": "Do something.",
            "starter_code": "# Write\n",
            "solution_code": "print('done')\n",
            "test_cases": [
                {
                    "input": "",
                    "expected_output": "done\n",
                    "comparison_type": "exact",
                }
            ],
            "order": 1,
        }
    ]
    (lesson_dir / "exercises.json").write_text(
        json.dumps(exercises), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def content_dir(tmp_path: Path) -> Path:
    """Build a temporary content directory with a manifest and lesson files."""
    lessons = [
        {"slug": "lesson-1", "title": "Getting Started", "order": 1, "path": "python"},
        {"slug": "lesson-2", "title": "Variables", "order": 2, "path": "python"},
        {"slug": "lesson-3", "title": "Loops", "order": 3, "path": "python"},
    ]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(lessons), encoding="utf-8")

    for lesson in lessons:
        _write_lesson(tmp_path, lesson)

    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_seed_empty_database(content_dir: Path, db_session: AsyncSession):
    """A completely empty database should seed all lessons from the manifest."""
    result = await seed_content(session=db_session, content_dir=content_dir)

    assert result["status"] == "seeded"
    assert result["lessons_added"] == 3
    assert result["exercises_added"] == 3  # one exercise per lesson

    # Verify data made it to the DB
    count_result = await db_session.execute(select(func.count(Lesson.id)))
    assert count_result.scalar() == 3

    ex_result = await db_session.execute(select(func.count(Exercise.id)))
    assert ex_result.scalar() == 3


@pytest.mark.asyncio
async def test_seed_incremental_add_new_lessons(content_dir: Path, db_session: AsyncSession):
    """When some lessons exist, new ones from the manifest should be added."""
    # First seed: adds all 3 lessons
    result1 = await seed_content(session=db_session, content_dir=content_dir)
    assert result1["status"] == "seeded"

    # Add a 4th lesson to the manifest
    extra_lesson = {
        "slug": "lesson-4",
        "title": "Functions",
        "order": 4,
        "path": "python",
    }
    manifest_path = content_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.append(extra_lesson)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    # Create content for the new lesson
    _write_lesson(content_dir, extra_lesson)

    # Second seed: should detect the new lesson and add it
    result2 = await seed_content(session=db_session, content_dir=content_dir)

    assert result2["status"] == "synced_with_new"
    assert result2["lessons_added"] == 1
    assert result2["exercises_added"] == 1
    assert "lessons_existing" in result2

    # Verify total is now 4
    count_result = await db_session.execute(select(func.count(Lesson.id)))
    assert count_result.scalar() == 4


@pytest.mark.asyncio
async def test_seed_multiple_new_lessons_incremental(content_dir: Path, db_session: AsyncSession):
    """Adding multiple new lessons at once should seed all of them."""
    # First seed
    await seed_content(session=db_session, content_dir=content_dir)

    # Add 2 new lessons
    manifest_path = content_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for i in (4, 5):
        lesson = {"slug": f"lesson-{i}", "title": f"Lesson {i}", "order": i, "path": "python"}
        manifest.append(lesson)
        _write_lesson(content_dir, lesson)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = await seed_content(session=db_session, content_dir=content_dir)
    assert result["status"] == "synced_with_new"
    assert result["lessons_added"] == 2
    assert result["exercises_added"] == 2


@pytest.mark.asyncio
async def test_seed_no_new_lessons(content_dir: Path, db_session: AsyncSession):
    """When all manifest lessons already exist, just sync test cases."""
    # First seed
    await seed_content(session=db_session, content_dir=content_dir)

    # Second seed with same manifest
    result = await seed_content(session=db_session, content_dir=content_dir)

    assert result["status"] == "synced"
    assert result["lessons_existing"] == 3
    assert "exercises_synced" in result


@pytest.mark.asyncio
async def test_seed_syncs_test_cases_on_existing(content_dir: Path, db_session: AsyncSession):
    """Existing exercises should have test_cases synced from content files."""
    # First seed
    await seed_content(session=db_session, content_dir=content_dir)

    # Modify test_cases in the content file
    ex_path = content_dir / "python" / "lesson-1" / "exercises.json"
    exercises = json.loads(ex_path.read_text(encoding="utf-8"))
    exercises[0]["test_cases"][0]["expected_output"] = "modified\n"
    ex_path.write_text(json.dumps(exercises), encoding="utf-8")

    # Re-seed
    result = await seed_content(session=db_session, content_dir=content_dir)

    assert result["status"] == "synced"
    assert result["exercises_synced"] == 1

    # Verify the DB was updated
    result_ex = await db_session.execute(
        select(Exercise).where(Exercise.slug == "lesson-1-ex1")
    )
    db_ex = result_ex.scalar_one()
    assert db_ex.test_cases[0]["expected_output"] == "modified\n"


@pytest.mark.asyncio
async def test_seed_missing_content_dir():
    """Should return an error when the content directory doesn't exist."""
    result = await seed_content(content_dir=Path("/nonexistent/"))
    assert "error" in result
    assert "Content directory not found" in result["error"]


@pytest.mark.asyncio
async def test_seed_missing_manifest(tmp_path: Path):
    """Should return an error when manifest.json doesn't exist."""
    result = await seed_content(content_dir=tmp_path)
    assert "error" in result
    assert "Manifest not found" in result["error"]


@pytest.mark.asyncio
async def test_seed_lesson_without_exercises(content_dir: Path, db_session: AsyncSession):
    """A lesson without exercises.json should still seed the lesson with 0 exercises."""
    manifest_path = content_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    # Add a lesson with no exercises file
    no_ex = {"slug": "no-ex-lesson", "title": "No Exercises", "order": 10, "path": "python"}
    manifest.append(no_ex)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    lesson_dir = content_dir / "python" / "no-ex-lesson"
    lesson_dir.mkdir(parents=True)
    (lesson_dir / "lesson.md").write_text("# No Exercises\n\nNo exercises here.\n", encoding="utf-8")
    # Deliberately no exercises.json

    result = await seed_content(session=db_session, content_dir=content_dir)

    assert result["status"] == "seeded"
    assert result["lessons_added"] == 4
    assert result["exercises_added"] == 3  # only the original 3 have exercises

    db_lesson = await db_session.execute(
        select(Lesson).where(Lesson.slug == "no-ex-lesson")
    )
    assert db_lesson.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_seed_empty_exercises_list(content_dir: Path, db_session: AsyncSession):
    """A lesson with an empty exercises list should seed correctly."""
    manifest_path = content_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    empty_ex = {"slug": "empty-ex-lesson", "title": "Empty Exercises", "order": 10, "path": "python"}
    manifest.append(empty_ex)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    lesson_dir = content_dir / "python" / "empty-ex-lesson"
    lesson_dir.mkdir(parents=True)
    (lesson_dir / "lesson.md").write_text("# Empty\n\nContent.\n", encoding="utf-8")
    (lesson_dir / "exercises.json").write_text("[]", encoding="utf-8")

    result = await seed_content(session=db_session, content_dir=content_dir)

    assert result["status"] == "seeded"
    assert result["lessons_added"] == 4
    assert result["exercises_added"] == 3  # original 3 only


@pytest.mark.asyncio
async def test_seed_skips_already_existing_when_adding_new(content_dir: Path, db_session: AsyncSession):
    """When adding new lessons, already-existing slugs should be skipped."""
    # Seed initial
    await seed_content(session=db_session, content_dir=content_dir)

    # Add a duplicate slug and a genuinely new one
    manifest_path = content_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.append({
        "slug": "lesson-1",  # Already exists!
        "title": "Duplicate",
        "order": 99,
        "path": "python",
    })
    manifest.append({
        "slug": "brand-new",
        "title": "Brand New",
        "order": 100,
        "path": "python",
    })
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    _write_lesson(content_dir, {"slug": "brand-new", "title": "Brand New", "order": 100, "path": "python"})

    result = await seed_content(session=db_session, content_dir=content_dir)

    assert result["status"] == "synced_with_new"
    assert result["lessons_added"] == 1  # Only brand-new, not lesson-1 duplicate
    assert result["exercises_added"] == 1  # _write_lesson creates 1 exercise per lesson


@pytest.mark.asyncio
async def test_seed_same_exercise_slug_different_lessons(
    tmp_path: Path, db_session: AsyncSession
):
    """Two different lessons may have exercises with the same slug.

    Previously, Exercise.slug had a global UNIQUE constraint. With the fix,
    uniqueness is per (lesson_id, slug), so two different lessons can share
    exercise slugs without conflict. This simulates the exact scenario that
    crashed seed_content() after lesson renumbering.
    """
    manifest = [
        {"slug": "old-api-lesson", "title": "Old API Lesson", "order": 1, "path": "api"},
    ]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    # Old lesson with exercise slug "build-json-payload"
    old_dir = _lesson_dir(tmp_path, "api", "old-api-lesson")
    old_dir.mkdir(parents=True)
    (old_dir / "lesson.md").write_text("# Old API Lesson\n\nContent.\n", encoding="utf-8")
    old_exercises = [
        {
            "slug": "build-json-payload",
            "title": "Build a JSON payload",
            "instruction": "Do something.",
            "starter_code": "# Write\n",
            "solution_code": "print('done')\n",
            "test_cases": [{"input": "", "expected_output": "done\n", "comparison_type": "exact"}],
            "order": 1,
        }
    ]
    (old_dir / "exercises.json").write_text(json.dumps(old_exercises), encoding="utf-8")

    # Seed the old lesson
    result1 = await seed_content(session=db_session, content_dir=tmp_path)
    assert result1["status"] == "seeded"
    assert result1["lessons_added"] == 1
    assert result1["exercises_added"] == 1

    # Now add a new lesson with the SAME exercise slug (the renumbering scenario)
    manifest.append(
        {"slug": "19-json-api-payloads", "title": "Handling JSON Payloads", "order": 2, "path": "api"}
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    new_dir = _lesson_dir(tmp_path, "api", "19-json-api-payloads")
    new_dir.mkdir(parents=True)
    (new_dir / "lesson.md").write_text("# JSON API Payloads\n\nContent.\n", encoding="utf-8")
    new_exercises = [
        {
            "slug": "build-json-payload",  # Same slug as old lesson!
            "title": "Build a JSON payload for an API request",
            "instruction": "Do something else.",
            "starter_code": "# Write\n",
            "solution_code": "print('ok')\n",
            "test_cases": [{"input": "", "expected_output": "ok\n", "comparison_type": "exact"}],
            "order": 1,
        },
        {
            "slug": "parse-api-response",
            "title": "Parse a simulated API response",
            "instruction": "Parse it.",
            "starter_code": "# Write\n",
            "solution_code": "print('parsed')\n",
            "test_cases": [],
            "order": 2,
        },
    ]
    (new_dir / "exercises.json").write_text(json.dumps(new_exercises), encoding="utf-8")

    # Seed again — this must NOT crash with UNIQUE constraint violation
    result2 = await seed_content(session=db_session, content_dir=tmp_path)

    assert result2["status"] == "synced_with_new"
    assert result2["lessons_added"] == 1
    assert result2["exercises_added"] == 2

    # Verify both lessons have their exercises
    old_lesson = (
        await db_session.execute(select(Lesson).where(Lesson.slug == "old-api-lesson"))
    ).scalar_one()
    new_lesson = (
        await db_session.execute(select(Lesson).where(Lesson.slug == "19-json-api-payloads"))
    ).scalar_one()

    old_ex = (
        await db_session.execute(
            select(Exercise).where(
                Exercise.slug == "build-json-payload",
                Exercise.lesson_id == old_lesson.id,
            )
        )
    ).scalar_one()
    assert old_ex is not None
    assert old_ex.title == "Build a JSON payload"  # Old lesson's version

    new_ex = (
        await db_session.execute(
            select(Exercise).where(
                Exercise.slug == "build-json-payload",
                Exercise.lesson_id == new_lesson.id,
            )
        )
    ).scalar_one()
    assert new_ex is not None
    assert new_ex.title == "Build a JSON payload for an API request"  # New lesson's version

    # There should be exactly 3 exercises total across both lessons
    count_result = await db_session.execute(select(func.count(Exercise.id)))
    assert count_result.scalar() == 3


@pytest.mark.asyncio
async def test_seed_nested_manifest(
    tmp_path: Path, db_session: AsyncSession
):
    """Manifest inside a python/ subdirectory (the restructured layout).

    After the content was reorganised from ``content/manifest.json`` to
    ``content/python/manifest.json``, the seed function must find the
    nested manifest via ``_find_manifest()`` and still resolve lesson
    paths correctly.
    """
    # Build a nested structure:  tmp_path/python/manifest.json
    #                             tmp_path/python/lesson-a/lesson.md  etc.
    lessons = [
        {"slug": "nested-lesson-a", "title": "Nested A", "order": 1, "path": "python"},
        {"slug": "nested-lesson-b", "title": "Nested B", "order": 2, "path": "python"},
    ]
    language_dir = tmp_path / "python"
    language_dir.mkdir()
    manifest_path = language_dir / "manifest.json"
    manifest_path.write_text(json.dumps(lessons), encoding="utf-8")

    for lesson in lessons:
        _write_lesson(tmp_path, lesson)

    result = await seed_content(session=db_session, content_dir=tmp_path)

    assert result["status"] == "seeded"
    assert result["lessons_added"] == 2
    assert result["exercises_added"] == 2

    # Verify data
    count_result = await db_session.execute(select(func.count(Lesson.id)))
    assert count_result.scalar() == 2
    ex_result = await db_session.execute(select(func.count(Exercise.id)))
    assert ex_result.scalar() == 2


@pytest.mark.asyncio
async def test_seed_nested_manifest_incremental(
    tmp_path: Path, db_session: AsyncSession
):
    """Incremental seeding works when manifest is in a python/ subdirectory."""
    language_dir = tmp_path / "python"
    language_dir.mkdir()

    # First seed
    lessons = [
        {"slug": "inc-a", "title": "Inc A", "order": 1, "path": "python"},
    ]
    manifest_path = language_dir / "manifest.json"
    manifest_path.write_text(json.dumps(lessons), encoding="utf-8")
    _write_lesson(tmp_path, lessons[0])

    result1 = await seed_content(session=db_session, content_dir=tmp_path)
    assert result1["status"] == "seeded"

    # Add a second lesson
    lessons.append({"slug": "inc-b", "title": "Inc B", "order": 2, "path": "python"})
    manifest_path.write_text(json.dumps(lessons), encoding="utf-8")
    _write_lesson(tmp_path, lessons[1])

    result2 = await seed_content(session=db_session, content_dir=tmp_path)
    assert result2["status"] == "synced_with_new"
    assert result2["lessons_added"] == 1
    assert result2["exercises_added"] == 1
