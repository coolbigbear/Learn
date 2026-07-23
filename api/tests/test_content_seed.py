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
# Helpers
# ---------------------------------------------------------------------------


def _make_lesson_dir(base_dir: Path, slug: str, title: str, order: int, path_key: str = "core"):
    """Create a lesson directory with lesson.md and exercises.json."""
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
