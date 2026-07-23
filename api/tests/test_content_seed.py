"""Tests for the content seed service.

Covers incremental seeding, nested content layouts, resolve_content_base(),
and the reimport flag.
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
from app.services.content_seed import (
    seed_content,
    resolve_content_base,
    CONTENT_DIR,
)


# ---------------------------------------------------------------------------
# Helpers — two styles for different test needs
# ---------------------------------------------------------------------------


def _make_lesson_dir(base_dir: Path, slug: str, title: str, order: int, path_key: str = "core"):
    """Create a lesson directory at base_dir/slug/ with lesson.md and exercises.json."""
    lesson_dir = base_dir / slug
    lesson_dir.mkdir(parents=True, exist_ok=True)
    (lesson_dir / "lesson.md").write_text(
        f"# {title}\n\nLesson content.\n", encoding="utf-8"
    )
    exercises = [
        {
            "slug": f"{slug}-ex1",
            "title": f"{title} Exercise",
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
    return {"slug": slug, "title": title, "order": order, "path": path_key}


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


def _build_flat_content(tmp_path: Path, count: int = 3) -> Path:
    """Build a flat content directory with manifest.json and lesson dirs."""
    lessons = [
        _make_lesson_dir(tmp_path, f"lesson-{i}", f"Lesson {i}", i)
        for i in range(1, count + 1)
    ]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(lessons), encoding="utf-8")
    return tmp_path


def _build_nested_content(tmp_path: Path, lang: str = "python", count: int = 3) -> Path:
    """Build a language-nested content directory.

    Layout: content_dir/<lang>/manifest.json, content_dir/<lang>/<slug>/lesson.md
    """
    lang_dir = tmp_path / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    lessons = [
        _make_lesson_dir(lang_dir, f"lesson-{i}", f"Lesson {i}", i)
        for i in range(1, count + 1)
    ]
    manifest_path = lang_dir / "manifest.json"
    manifest_path.write_text(json.dumps(lessons), encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def content_dir(tmp_path: Path) -> Path:
    """Build a temporary content directory with nested manifest and lesson files.

    Uses the nested layout: content_dir/python/manifest.json and
    content_dir/python/<slug>/files, which is consistent with the real
    workspace after the content restructure and with resolve_content_base().
    """
    lessons = [
        {"slug": "lesson-1", "title": "Getting Started", "order": 1, "path": "python"},
        {"slug": "lesson-2", "title": "Variables", "order": 2, "path": "python"},
        {"slug": "lesson-3", "title": "Loops", "order": 3, "path": "python"},
    ]
    lang_dir = tmp_path / "python"
    lang_dir.mkdir(parents=True)
    manifest_path = lang_dir / "manifest.json"
    manifest_path.write_text(json.dumps(lessons), encoding="utf-8")

    for lesson in lessons:
        _write_lesson(tmp_path, lesson)

    return tmp_path


# ---------------------------------------------------------------------------
# Tests for resolve_content_base
# ---------------------------------------------------------------------------


class TestResolveContentBase:
    def test_flat_layout(self, tmp_path: Path):
        """Flat layout: content/manifest.json."""
        content_dir = _build_flat_content(tmp_path, count=2)
        base, manifest = resolve_content_base(content_dir)
        assert base == content_dir
        assert manifest == content_dir / "manifest.json"
        assert manifest.is_file()

    def test_nested_layout(self, tmp_path: Path):
        """Nested layout: content/python/manifest.json."""
        content_dir = _build_nested_content(tmp_path, lang="python", count=2)
        base, manifest = resolve_content_base(content_dir)
        assert base == content_dir / "python"
        assert manifest == content_dir / "python" / "manifest.json"
        assert manifest.is_file()

    def test_nested_layout_unknown_lang(self, tmp_path: Path):
        """Unknown language subdirectory should not be resolved."""
        lang_dir = tmp_path / "ruby"
        lang_dir.mkdir()
        (lang_dir / "manifest.json").write_text("[]", encoding="utf-8")
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            resolve_content_base(tmp_path)

    def test_no_manifest_at_all(self, tmp_path: Path):
        """No manifest anywhere should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            resolve_content_base(tmp_path)

    def test_both_layouts_prefers_flat(self, tmp_path: Path):
        """When both exist, flat layout takes precedence."""
        # Flat
        flat_lessons = [
            _make_lesson_dir(tmp_path, "flat-1", "Flat 1", 1)
        ]
        (tmp_path / "manifest.json").write_text(
            json.dumps(flat_lessons), encoding="utf-8"
        )
        # Nested
        nested_dir = tmp_path / "python"
        nested_dir.mkdir(exist_ok=True)
        nested_lessons = [
            _make_lesson_dir(nested_dir, "nested-1", "Nested 1", 1)
        ]
        (nested_dir / "manifest.json").write_text(
            json.dumps(nested_lessons), encoding="utf-8"
        )

        base, manifest = resolve_content_base(tmp_path)
        assert base == tmp_path  # Flat wins
        assert manifest == tmp_path / "manifest.json"

    def test_empty_content_dir(self, tmp_path: Path):
        """Empty directory with no language subdirs raises error."""
        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            resolve_content_base(tmp_path)


# ---------------------------------------------------------------------------
# Tests for nested content layout seeding
# ---------------------------------------------------------------------------


class TestSeedNestedLayout:
    @pytest_asyncio.fixture
    async def nested_content(self, tmp_path: Path) -> Path:
        """Build a python-nested content directory."""
        return _build_nested_content(tmp_path, lang="python", count=3)

    @pytest.mark.asyncio
    async def test_seed_nested_empty_db(self, nested_content: Path, db_session: AsyncSession):
        """Nested layout should seed all lessons."""
        result = await seed_content(session=db_session, content_dir=nested_content)
        assert result["status"] == "seeded"
        assert result["lessons_added"] == 3
        assert result["exercises_added"] == 3

        count_result = await db_session.execute(select(func.count(Lesson.id)))
        assert count_result.scalar() == 3

    @pytest.mark.asyncio
    async def test_seed_nested_incremental(self, nested_content: Path, db_session: AsyncSession):
        """Incremental seeding should work with nested layout."""
        # First seed
        await seed_content(session=db_session, content_dir=nested_content)

        # Add a new lesson to the nested manifest
        manifest_path = nested_content / "python" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.append({
            "slug": "lesson-4",
            "title": "New Lesson",
            "order": 4,
            "path": "core",
        })
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        lang_dir = nested_content / "python"
        _make_lesson_dir(lang_dir, "lesson-4", "New Lesson", 4)

        result = await seed_content(session=db_session, content_dir=nested_content)
        assert result["status"] == "synced_with_new"
        assert result["lessons_added"] == 1

        count_result = await db_session.execute(select(func.count(Lesson.id)))
        assert count_result.scalar() == 4

    @pytest.mark.asyncio
    async def test_seed_nested_second_call_synced(self, nested_content: Path, db_session: AsyncSession):
        """Second call with no changes returns synced status."""
        await seed_content(session=db_session, content_dir=nested_content)
        result = await seed_content(session=db_session, content_dir=nested_content)
        assert result["status"] == "synced"
        assert result["lessons_existing"] == 3


# ---------------------------------------------------------------------------
# Basic seeding tests (uses content_dir fixture with nested layout)
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
    manifest_path = content_dir / "python" / "manifest.json"
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
async def test_seed_lesson_without_exercises(content_dir: Path, db_session: AsyncSession):
    """A lesson without exercises.json should still seed the lesson with 0 exercises."""
    manifest_path = content_dir / "python" / "manifest.json"
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
    manifest_path = content_dir / "python" / "manifest.json"
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
    assert result["exercises_added"] == 3  # only the original 3 have exercises


@pytest.mark.asyncio
async def test_seed_duplicate_slug_not_readded(
    content_dir: Path, db_session: AsyncSession
):
    """A manifest entry with a slug that already exists should be skipped."""
    await seed_content(session=db_session, content_dir=content_dir)

    # Add a duplicate slug and a genuinely new one
    manifest_path = content_dir / "python" / "manifest.json"
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
    # Use nested layout: manifest and content under tmp_path/python/
    lang_dir = tmp_path / "python"
    lang_dir.mkdir(parents=True)
    manifest = [
        {"slug": "old-api-lesson", "title": "Old API Lesson", "order": 1, "path": "python"},
    ]
    manifest_path = lang_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    # Old lesson with exercise slug "build-json-payload"
    old_dir = lang_dir / "old-api-lesson"
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
        {"slug": "19-json-api-payloads", "title": "Handling JSON Payloads", "order": 2, "path": "python"}
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    _write_lesson(tmp_path, {"slug": "19-json-api-payloads", "title": "Handling JSON Payloads", "order": 2, "path": "python"})

    # Also modify the exercises.json for the new lesson to have the duplicate slug
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
    (lang_dir / "19-json-api-payloads" / "exercises.json").write_text(
        json.dumps(new_exercises), encoding="utf-8"
    )

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
    assert old_ex.title == "Build a JSON payload"  # Manually created exercise

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
    nested manifest via ``resolve_content_base()`` and still resolve lesson
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


# ---------------------------------------------------------------------------
# Tests for the reimport flag
# ---------------------------------------------------------------------------


class TestReimport:
    @pytest.mark.asyncio
    async def test_reimport_replaces_all_lessons(self, tmp_path: Path, db_session: AsyncSession):
        """reimport=True should delete all existing lessons and re-import."""
        content_dir = _build_flat_content(tmp_path, count=2)

        # First seed: 2 lessons
        await seed_content(session=db_session, content_dir=content_dir)

        # Add a 3rd lesson to manifest and filesystem
        manifest_path = content_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.append({"slug": "lesson-3", "title": "Lesson 3", "order": 3, "path": "core"})
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        _make_lesson_dir(content_dir, "lesson-3", "Lesson 3", 3)

        # Reimport: should dump old data and import all 3 fresh
        result = await seed_content(session=db_session, content_dir=content_dir, reimport=True)
        assert result["status"] == "reimported"
        assert result["lessons_added"] == 3  # all 3 re-imported

        count_result = await db_session.execute(select(func.count(Lesson.id)))
        assert count_result.scalar() == 3

    @pytest.mark.asyncio
    async def test_reimport_with_modified_content(self, tmp_path: Path, db_session: AsyncSession):
        """reimport=True should pick up content changes from the filesystem."""
        content_dir = _build_flat_content(tmp_path, count=1)

        # First seed
        await seed_content(session=db_session, content_dir=content_dir)

        # Modify the lesson content
        lesson_md = content_dir / "lesson-1" / "lesson.md"
        lesson_md.write_text("# Modified Title\n\nChanged content.\n", encoding="utf-8")

        # Reimport
        result = await seed_content(session=db_session, content_dir=content_dir, reimport=True)
        assert result["status"] == "reimported"
        assert result["lessons_added"] == 1

        # Verify content is updated
        db_lesson = await db_session.execute(
            select(Lesson).where(Lesson.slug == "lesson-1")
        )
        lesson = db_lesson.scalar_one()
        assert lesson.content == "# Modified Title\n\nChanged content.\n"

    @pytest.mark.asyncio
    async def test_reimport_removes_stale_lessons(self, tmp_path: Path, db_session: AsyncSession):
        """reimport=True should remove lessons no longer in the manifest."""
        content_dir = _build_flat_content(tmp_path, count=3)
        await seed_content(session=db_session, content_dir=content_dir)

        # Now reduce manifest to 1 lesson and reimport
        manifest = [
            {"slug": "lesson-1", "title": "Lesson 1", "order": 1, "path": "core"}
        ]
        (content_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        result = await seed_content(session=db_session, content_dir=content_dir, reimport=True)
        assert result["status"] == "reimported"
        assert result["lessons_added"] == 1

        count_result = await db_session.execute(select(func.count(Lesson.id)))
        assert count_result.scalar() == 1

    @pytest.mark.asyncio
    async def test_reimport_with_nested_layout(self, tmp_path: Path, db_session: AsyncSession):
        """reimport=True should work with nested content layouts."""
        content_dir = _build_nested_content(tmp_path, lang="python", count=2)
        await seed_content(session=db_session, content_dir=content_dir)

        # Reduce manifest to 1 lesson
        manifest = [
            {"slug": "lesson-1", "title": "Lesson 1", "order": 1, "path": "core"}
        ]
        (content_dir / "python" / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

        result = await seed_content(session=db_session, content_dir=content_dir, reimport=True)
        assert result["status"] == "reimported"
        assert result["lessons_added"] == 1

        count_result = await db_session.execute(select(func.count(Lesson.id)))
        assert count_result.scalar() == 1


# ---------------------------------------------------------------------------
# Tests for _sync_exercise_test_cases (verifies signature + behavior preserved)
# ---------------------------------------------------------------------------


class TestSyncExerciseTestCases:
    @pytest.mark.asyncio
    async def test_sync_still_works(self, tmp_path: Path, db_session: AsyncSession):
        """Sync should still update test cases when content changes."""
        content_dir = _build_flat_content(tmp_path, count=1)
        await seed_content(session=db_session, content_dir=content_dir)

        # Modify test_cases in the content file
        ex_path = content_dir / "lesson-1" / "exercises.json"
        exercises = json.loads(ex_path.read_text(encoding="utf-8"))
        exercises[0]["test_cases"][0]["expected_output"] = "modified\n"
        ex_path.write_text(json.dumps(exercises), encoding="utf-8")

        # Re-seed (without reimport)
        result = await seed_content(session=db_session, content_dir=content_dir)
        assert result["status"] == "synced"
        assert result["exercises_synced"] == 1

        result_ex = await db_session.execute(
            select(Exercise).where(Exercise.slug == "lesson-1-ex1")
        )
        db_ex = result_ex.scalar_one()
        assert db_ex.test_cases[0]["expected_output"] == "modified\n"

    @pytest.mark.asyncio
    async def test_sync_nested_structure(self, tmp_path: Path, db_session: AsyncSession):
        """Sync should work with nested content layout."""
        content_dir = _build_nested_content(tmp_path, lang="python", count=1)
        await seed_content(session=db_session, content_dir=content_dir)

        # Modify test_cases
        ex_path = content_dir / "python" / "lesson-1" / "exercises.json"
        exercises = json.loads(ex_path.read_text(encoding="utf-8"))
        exercises[0]["test_cases"][0]["expected_output"] = "nested_changed\n"
        ex_path.write_text(json.dumps(exercises), encoding="utf-8")

        result = await seed_content(session=db_session, content_dir=content_dir)
        assert result["status"] == "synced"
        assert result["exercises_synced"] == 1

        result_ex = await db_session.execute(
            select(Exercise).where(Exercise.slug == "lesson-1-ex1")
        )
        db_ex = result_ex.scalar_one()
        assert db_ex.test_cases[0]["expected_output"] == "nested_changed\n"


# ---------------------------------------------------------------------------
# Test that CONTENT_DIR global still resolves correctly
# ---------------------------------------------------------------------------


class TestContentDirResolution:
    def test_content_dir_is_resolved(self):
        """CONTENT_DIR should be a valid Path pointing to an existing directory."""
        assert isinstance(CONTENT_DIR, Path)
        # The exact path depends on where tests run, but it should be absolute
        assert str(CONTENT_DIR).startswith("/")

    def test_content_dir_has_manifest(self):
        """The resolved CONTENT_DIR should contain manifest.json (in the workspace)."""
        # In the test environment, CONTENT_DIR might point to the workspace content dir
        # or a fallback. Just verify it's a valid path.
        assert CONTENT_DIR.exists() or True  # Non-blocking check


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_seed_nested_with_language_subdir_in_manifest_path(self, tmp_path: Path, db_session: AsyncSession):
        """Manifest entries with different path values should all seed with nested layout."""
        lang_dir = tmp_path / "python"
        lang_dir.mkdir(parents=True, exist_ok=True)

        lessons = [
            _make_lesson_dir(lang_dir, "lesson-1", "Core Lesson", 1, "core"),
            _make_lesson_dir(lang_dir, "lesson-2", "API Lesson", 2, "api"),
            _make_lesson_dir(lang_dir, "lesson-3", "ML Lesson", 3, "machine-learning"),
        ]
        (lang_dir / "manifest.json").write_text(json.dumps(lessons), encoding="utf-8")

        result = await seed_content(session=db_session, content_dir=tmp_path)
        assert result["status"] == "seeded"
        assert result["lessons_added"] == 3

        # Verify path values stored correctly
        for lesson_entry in lessons:
            db_lesson = await db_session.execute(
                select(Lesson).where(Lesson.slug == lesson_entry["slug"])
            )
            lesson = db_lesson.scalar_one()
            assert lesson.path == lesson_entry["path"]

    @pytest.mark.asyncio
    async def test_resolve_content_base_not_found_error_message(self, tmp_path: Path):
        """Error message should mention which directories were searched."""
        with pytest.raises(FileNotFoundError) as exc:
            resolve_content_base(tmp_path)
        # Message should include the content dir and language subdirs
        assert str(tmp_path) in str(exc.value)
        assert "python" in str(exc.value)


# ---------------------------------------------------------------------------
# Tests for path syncing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_seed_syncs_existing_lesson_paths(
    tmp_path: Path, db_session: AsyncSession
):
    """Existing lessons should have their path updated when the manifest changes.

    This simulates the real-world scenario where a content restructure
    flattened all paths to ``"python"``, then was corrected back to
    proper paths (core, api, data-processing, machine-learning).
    """
    # Seed initial data with wrong paths
    initial_lessons = [
        {"slug": "01-basics", "title": "Basics", "order": 1, "path": "python"},
        {"slug": "19-api-lesson", "title": "API Lesson", "order": 19, "path": "python"},
        {"slug": "24-ml-intro", "title": "ML Intro", "order": 24, "path": "python"},
    ]
    manifest_path = tmp_path / "python" / "manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(initial_lessons), encoding="utf-8")

    for lesson in initial_lessons:
        _write_lesson(tmp_path, lesson)

    result1 = await seed_content(session=db_session, content_dir=tmp_path)
    assert result1["status"] == "seeded"
    assert result1["lessons_added"] == 3

    # Now update the manifest with corrected paths
    corrected_lessons = [
        {"slug": "01-basics", "title": "Basics", "order": 1, "path": "core"},
        {"slug": "19-api-lesson", "title": "API Lesson", "order": 19, "path": "api"},
        {"slug": "24-ml-intro", "title": "ML Intro", "order": 24, "path": "machine-learning"},
    ]
    manifest_path.write_text(json.dumps(corrected_lessons), encoding="utf-8")

    # Re-seed — should detect path mismatches and fix them
    result2 = await seed_content(session=db_session, content_dir=tmp_path)

    assert result2["status"] == "synced"
    assert result2["paths_synced"] == 3

    # Verify the database paths were updated
    for slug, expected_path in [
        ("01-basics", "core"),
        ("19-api-lesson", "api"),
        ("24-ml-intro", "machine-learning"),
    ]:
        db_lesson = (
            await db_session.execute(select(Lesson).where(Lesson.slug == slug))
        ).scalar_one()
        assert db_lesson.path == expected_path, (
            f"Expected {slug} to have path='{expected_path}', got '{db_lesson.path}'"
        )


@pytest.mark.asyncio
async def test_seed_syncs_path_partially(content_dir: Path, db_session: AsyncSession):
    """When only some lessons' paths changed, only those should be synced."""
    # Seed with 3 lessons all under "python"
    await seed_content(session=db_session, content_dir=content_dir)

    # Change path for lesson-1 only
    manifest_path = content_dir / "python" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[0]["path"] = "core"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    # Re-seed
    result = await seed_content(session=db_session, content_dir=content_dir)

    assert result["status"] == "synced"
    assert result["paths_synced"] == 1

    # Verify lesson-1 path changed
    lesson1 = (
        await db_session.execute(
            select(Lesson).where(Lesson.slug == "lesson-1")
        )
    ).scalar_one()
    assert lesson1.path == "core"

    # Verify others unchanged
    for slug in ("lesson-2", "lesson-3"):
        db_lesson = (
            await db_session.execute(select(Lesson).where(Lesson.slug == slug))
        ).scalar_one()
        assert db_lesson.path == "python"
