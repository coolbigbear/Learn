"""Auto-seed lessons and exercises from the content directory on first start.

Called during FastAPI startup lifecycle. Idempotent -- only inserts lessons
that don't already exist in the database. Safe to call on every container start.

When lessons already exist, the function detects new lessons in the manifest
that haven't been seeded yet, adds them, and syncs exercise test_cases for
existing lessons.
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


async def _get_existing_lesson_slugs(session: AsyncSession) -> set[str]:
    """Return the set of lesson slugs already in the database."""
    result = await session.execute(select(Lesson.slug))
    return {row[0] for row in result.all()}


async def _sync_exercise_test_cases(session: AsyncSession) -> int:
    """Sync exercise test_cases from content files to DB.

    Reads content/<lesson>/exercises.json for each lesson in the manifest and
    updates the database if any exercise's test_cases differ. Returns count of
    updates made.
    """
    manifest_path = CONTENT_DIR / "manifest.json"
    if not manifest_path.is_file():
        return 0

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    update_count = 0

    for entry in manifest:
        slug = entry["slug"]
        exercises_json_path = CONTENT_DIR / slug / "exercises.json"
        if not exercises_json_path.is_file():
            continue

        exercises_data = json.loads(exercises_json_path.read_text(encoding="utf-8"))

        for content_ex in exercises_data:
            ex_slug = content_ex["slug"]
            content_test_cases = content_ex.get("test_cases", [])

            result = await session.execute(
                select(Exercise).where(Exercise.slug == ex_slug)
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
    session: AsyncSession, entry: dict
) -> tuple[int, int]:
    """Insert a single lesson and its exercises from the manifest entry.

    Returns (lessons_added, exercises_added).
    """
    slug = entry["slug"]
    title = entry["title"]
    order = entry["order"]
    path_key = entry.get("path", "core")

    # Read lesson content
    lesson_md = CONTENT_DIR / slug / "lesson.md"
    if not lesson_md.is_file():
        return 0, 0
    content = lesson_md.read_text(encoding="utf-8")

    lesson = Lesson(
        slug=slug,
        title=title,
        content=content,
        path=path_key,
        order=order,
    )
    session.add(lesson)
    await session.flush()  # Get lesson.id

    # Read exercises
    exercises_json = CONTENT_DIR / slug / "exercises.json"
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
) -> dict:
    """Import lesson content from content directory into the database.

    Parameters:
        session: Optional injected DB session for testing. When omitted, a new
                 session is created from ``async_session_factory``.
        content_dir: Optional override for the content directory path. When
                     omitted, uses ``CONTENT_DIR`` global.

    Returns a dict with counts of what was inserted/seeded/synced.

    On first run: inserts all lessons and exercises from the content files.
    On subsequent runs: detects new lessons in the manifest, adds them, and
    syncs exercise test_cases to match content files (handles expected_output
    changes after numpy/scipy updates, etc.).
    """
    if content_dir is None:
        content_dir = CONTENT_DIR

    if not content_dir.is_dir():
        return {"error": f"Content directory not found: {content_dir}"}

    manifest_path = content_dir / "manifest.json"
    if not manifest_path.is_file():
        return {"error": f"Manifest not found: {manifest_path}"}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    async def _work(session: AsyncSession) -> dict:
        existing_slugs = await _get_existing_lesson_slugs(session)
        new_entries = [e for e in manifest if e["slug"] not in existing_slugs]

        lessons_added = 0
        exercises_added = 0

        # Add new lessons
        for entry in new_entries:
            added_l, added_e = await _seed_lesson(session, entry)
            lessons_added += added_l
            exercises_added += added_e

        # Sync test cases for all existing exercises
        synced = await _sync_exercise_test_cases(session)

        if existing_slugs and not new_entries:
            # Existing data, nothing new to add
            return {
                "status": "synced",
                "reason": f"Lessons table already has {len(existing_slugs)} rows",
                "lessons_existing": len(existing_slugs),
                "exercises_synced": synced,
            }
        elif existing_slugs and new_entries:
            # Existing data plus new lessons added
            return {
                "status": "synced_with_new",
                "lessons_existing": len(existing_slugs),
                "lessons_added": lessons_added,
                "exercises_added": exercises_added,
                "exercises_synced": synced,
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
