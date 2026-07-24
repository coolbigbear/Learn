"""Auto-seed lessons and exercises from the content directory on first start.

Called during FastAPI startup lifecycle. Idempotent -- only inserts lessons
that don't already exist in the database. Safe to call on every container start.

When lessons already exist, the function detects new lessons in the manifest
that haven't been seeded yet, adds them, and syncs exercise test_cases for
existing lessons.

Supports both flat content layouts (content/manifest.json) and language-nested
layouts (content/python/manifest.json). Auto-detects the structure at runtime.
"""

import json
import os
from pathlib import Path

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.exercise import Exercise
from app.models.lesson import Lesson

# Resolve the content directory path.
# Supports three strategies in priority order:
#   1. CONTENT_DIR env var (explicit override, e.g. in docker-compose)
#   2. Derive from this file's location — works in both Docker and local dev
#   3. Hardcoded fallback (/app/content for backward compat with older images)
_content_env = os.environ.get("CONTENT_DIR")
if _content_env:
    CONTENT_DIR = Path(_content_env)
else:
    # File is at api/app/services/content_seed.py (or /app/app/services/ in Docker)
    _root = Path(__file__).resolve().parent.parent.parent.parent  # project root
    if not (_root / "api").is_dir():
        # Running inside Docker: /app/app/services/ → /app
        _root = Path(__file__).resolve().parent.parent.parent
    _candidate = _root / "content"
    CONTENT_DIR = _candidate if _candidate.is_dir() else Path("/app/content")

# Language subdirectories to probe when looking for nested content
# (e.g., content/python/, content/javascript/).
_LANGUAGE_SUBDIRS = ["python"]


def resolve_content_base(content_dir: Path) -> tuple[Path, Path]:
    """Resolve the base content directory and manifest path.

    Checks for manifest.json in both flat and language-nested layouts:

        Flat layout:   content/manifest.json
        Nested layout: content/python/manifest.json

    Returns (base_content_dir, manifest_path) where:
        base_content_dir — the directory containing lesson subdirectories
        manifest_path    — the full path to manifest.json

    Raises FileNotFoundError if no manifest is found.
    """
    # Check flat layout first (content/manifest.json)
    flat_manifest = content_dir / "manifest.json"
    if flat_manifest.is_file():
        return content_dir, flat_manifest

    # Check language-nested layouts (content/<lang>/manifest.json)
    for lang_dir in _LANGUAGE_SUBDIRS:
        nested_manifest = content_dir / lang_dir / "manifest.json"
        if nested_manifest.is_file():
            return content_dir / lang_dir, nested_manifest

    raise FileNotFoundError(
        f"Manifest not found in {content_dir} or any language subdirectory"
        f" ({', '.join(_LANGUAGE_SUBDIRS)})"
    )


def _find_manifest(content_dir: Path) -> Path | None:
    """Locate manifest.json in the content directory.

    Tries the direct path first, then falls back to looking inside
    language-subdirectories (e.g. ``content/python/manifest.json``) to
    support restructured content layouts where lessons were grouped
    under language folders.

    Returns the manifest Path if found, otherwise None.
    """
    direct = content_dir / "manifest.json"
    if direct.is_file():
        return direct
    # Fallback: scan immediate subdirectories for one that contains manifest.json
    if content_dir.is_dir():
        for sub in sorted(content_dir.iterdir()):
            if sub.is_dir():
                nested = sub / "manifest.json"
                if nested.is_file():
                    return nested
    return None


async def _get_existing_lesson_slugs(session: AsyncSession) -> set[str]:
    """Return the set of lesson slugs already in the database."""
    result = await session.execute(select(Lesson.slug))
    return {row[0] for row in result.all()}


async def _sync_existing_lesson_paths(
    session: AsyncSession, content_dir: Path
) -> int:
    """Update existing lessons' path column to match the manifest.

    When manifest paths are corrected (e.g. after a restructure that flattened
    all paths to ``"python"``), existing lessons in the database that were
    seeded with wrong or outdated paths get corrected. Returns count of
    updates made.
    """
    manifest_path = _find_manifest(content_dir)
    if manifest_path is None:
        return 0

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    update_count = 0

    for entry in manifest:
        slug = entry["slug"]
        expected_path = entry.get("path", "python")

        result = await session.execute(
            select(Lesson).where(Lesson.slug == slug)
        )
        lesson = result.scalar_one_or_none()
        if lesson is not None and lesson.path != expected_path:
            lesson.path = expected_path
            update_count += 1

    return update_count


async def _sync_exercise_test_cases(
    session: AsyncSession, base_dir: Path, manifest: list[dict]
) -> int:
    """Sync exercise test_cases from content files to DB.

    Reads base_dir/<lesson>/exercises.json for each lesson in the manifest and
    updates the database if any exercise's test_cases differ. Returns count of
    updates made.

    Uses lesson slug + exercise slug to uniquely identify exercises (the
    Exercise.slug is unique per lesson, not globally).

    Args:
        session: Database session.
        base_dir: The directory containing lesson subdirectories.
        manifest: Parsed manifest list of lesson entries.
    """
    update_count = 0

    for entry in manifest:
        slug = entry["slug"]
        exercises_json_path = base_dir / slug / "exercises.json"
        if not exercises_json_path.is_file():
            continue

        # Resolve the lesson ID for scoping exercise lookups
        lesson_result = await session.execute(
            select(Lesson).where(Lesson.slug == slug)
        )
        lesson = lesson_result.scalar_one_or_none()
        if lesson is None:
            continue

        exercises_data = json.loads(exercises_json_path.read_text(encoding="utf-8"))

        for content_ex in exercises_data:
            ex_slug = content_ex["slug"]
            content_test_cases = content_ex.get("test_cases", [])

            result = await session.execute(
                select(Exercise).where(
                    Exercise.slug == ex_slug,
                    Exercise.lesson_id == lesson.id,
                )
            )
            db_exercise = result.scalar_one_or_none()
            if db_exercise is None:
                continue

            db_test_cases = db_exercise.test_cases or []
            if db_test_cases != content_test_cases:
                db_exercise.test_cases = content_test_cases
                update_count += 1

    return update_count


async def _seed_lesson(
    session: AsyncSession, base_dir: Path, entry: dict
) -> tuple[int, int]:
    """Insert a single lesson and its exercises from the manifest entry.

    Args:
        session: Database session.
        base_dir: The directory containing lesson subdirectories.
        entry: A manifest entry dict with slug, title, order, path keys.

    Returns (lessons_added, exercises_added).
    """
    slug = entry["slug"]
    title = entry["title"]
    order = entry["order"]
    path_key = entry.get("path", "python")

    # Read lesson content
    lesson_md = base_dir / slug / "lesson.md"
    if not lesson_md.is_file():
        return 0, 0
    md_content = lesson_md.read_text(encoding="utf-8")

    lesson = Lesson(
        slug=slug,
        title=title,
        content=md_content,
        path=path_key,
        order=order,
    )
    session.add(lesson)
    await session.flush()  # Get lesson.id

    # Read exercises
    exercises_json = base_dir / slug / "exercises.json"
    if not exercises_json.is_file():
        return 1, 0

    exercises_data = json.loads(exercises_json.read_text(encoding="utf-8"))
    ex_count = 0
    for ex in exercises_data:
        exercise = Exercise(
            lesson_id=lesson.id,
            slug=ex["slug"],
            title=ex["title"],
            instruction=ex["instruction"],
            starter_code=ex.get("starter_code", "# Write your code here\n"),
            solution_code=ex.get("solution_code", ""),
            test_cases=ex.get("test_cases", []),
            language="python",
            order=ex["order"],
        )
        session.add(exercise)
        ex_count += 1

    return 1, ex_count


async def seed_content(
    session: AsyncSession | None = None,
    content_dir: Path | None = None,
    *,
    reimport: bool = False,
) -> dict:
    """Import lesson content from content directory into the database.

    Parameters:
        session: Optional injected DB session for testing. When omitted, a new
                 session is created from ``async_session_factory``.
        content_dir: Optional override for the content directory path. When
                     omitted, uses ``CONTENT_DIR`` global.
        reimport: If True, delete all existing lessons and exercises before
                  re-importing from the manifest. Useful for a full re-seed.

    Returns a dict with counts of what was inserted/seeded/synced.

    Supports both flat and language-nested content directory structures:

        Flat:   content/manifest.json, content/<slug>/lesson.md
        Nested: content/python/manifest.json, content/python/<slug>/lesson.md

    On first run: inserts all lessons and exercises from the content files.
    On subsequent runs: detects new lessons in the manifest, adds them, and
    syncs exercise test_cases to match content files (handles expected_output
    changes after numpy/scipy updates, etc.).
    """
    if content_dir is None:
        content_dir = CONTENT_DIR

    if not content_dir.is_dir():
        return {"error": f"Content directory not found: {content_dir}"}

    # Resolve manifest location (flat vs language-nested layout)
    try:
        base_dir, manifest_path = resolve_content_base(content_dir)
    except FileNotFoundError as e:
        return {"error": str(e)}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    async def _work(db: AsyncSession) -> dict:
        if reimport:
            # Full re-import: delete existing exercises and lessons.
            # Bulk DELETE bypasses ORM cascade, so we delete exercises first,
            # then lessons, to avoid FK / UNIQUE constraint violations.
            from sqlalchemy import delete as sa_delete

            await db.execute(sa_delete(Exercise))
            await db.execute(sa_delete(Lesson))
            existing_slugs: set[str] = set()
        else:
            existing_slugs = await _get_existing_lesson_slugs(db)

        new_entries = [e for e in manifest if e["slug"] not in existing_slugs]

        lessons_added = 0
        exercises_added = 0

        # Add new lessons
        for entry in new_entries:
            added_l, added_e = await _seed_lesson(db, base_dir, entry)
            lessons_added += added_l
            exercises_added += added_e

        # Sync test cases for existing exercises (skip on full reimport)
        synced = 0
        if not reimport:
            synced = await _sync_exercise_test_cases(db, base_dir, manifest)

        if reimport:
            return {
                "status": "reimported",
                "lessons_added": lessons_added,
                "exercises_added": exercises_added,
            }

        # Sync paths for existing lessons (e.g. after manifest path corrections)
        paths_synced = await _sync_existing_lesson_paths(db, content_dir)

        if existing_slugs and not new_entries:
            # Existing data, nothing new to add
            return {
                "status": "synced",
                "reason": f"Lessons table already has {len(existing_slugs)} rows",
                "lessons_existing": len(existing_slugs),
                "exercises_synced": synced,
                "paths_synced": paths_synced,
            }
        elif existing_slugs and new_entries:
            # Existing data plus new lessons added
            return {
                "status": "synced_with_new",
                "lessons_existing": len(existing_slugs),
                "lessons_added": lessons_added,
                "exercises_added": exercises_added,
                "exercises_synced": synced,
                "paths_synced": paths_synced,
            }
        else:
            # Fresh seed
            return {
                "status": "seeded",
                "lessons_added": lessons_added,
                "exercises_added": exercises_added,
            }

    if session is not None:
        return await _work(session)

    async with async_session_factory() as new_session:
        async with new_session.begin():
            return await _work(new_session)


async def _seed_all(session: AsyncSession) -> dict:
    """Legacy helper: seed all lessons from manifest (for fresh databases).

    Deprecated in favour of seed_content(). Kept for backward compatibility
    in case external callers reference it by name.
    """
    return await seed_content(session=session)
