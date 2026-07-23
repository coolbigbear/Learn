#!/usr/bin/env python3
"""Sync exercise test_cases from content JSON files to database.

Reads content/<lesson>/exercises.json for each lesson in the manifest and
updates the database if any exercise's test_cases differ. Reports what changed.

Usage (within Docker container):
    cd /app/api && python /app/scripts/sync_exercises.py

Usage (local dev, from api/ directory):
    python ../scripts/sync_exercises.py

Important: Run inside the same environment as the API (same DB, same venv).
For Docker deployments, use `docker exec`.
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure the api directory (or Docker's /app) is on the path
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
# Docker layout: /app/app/... (add /app to path)
if (_project_root / "app" / "app.py").exists() or (_project_root / "app" / "__init__.py").exists():
    sys.path.insert(0, str(_project_root))
# Local dev layout: <project>/api/app/... (add <project>/api to path)
_api_dir = _project_root / "api"
if _api_dir.is_dir():
    sys.path.insert(0, str(_api_dir))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Exercise, Lesson

# In Docker: DB at /app/api/../data/tutorials.db → /app/data/tutorials.db
# In local dev: DB at <project>/api/tutorials.db
CONTENT_DIR = _project_root / "content"
DATABASE_URL = "sqlite+aiosqlite:///./tutorials.db"
# Docker env: DATABASE_URL points to /app/data/tutorials.db
_alt_db = _project_root / "data" / "tutorials.db"
if _alt_db.exists():
    DATABASE_URL = f"sqlite+aiosqlite:///{_alt_db}"


async def sync() -> int:
    """Sync exercise test_cases from content files to DB. Returns count of updates."""
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Read manifest
    manifest_path = CONTENT_DIR / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: manifest not found at {manifest_path}")
        return 1

    with open(manifest_path) as f:
        manifest = json.load(f)

    update_count = 0

    async with session_factory() as session:
        for entry in manifest:
            slug = entry["slug"]
            path_key = entry.get("path", "python")
            exercises_json_path = CONTENT_DIR / path_key / slug / "exercises.json"
            if not exercises_json_path.exists():
                continue

            with open(exercises_json_path) as f:
                content_exercises = json.load(f)

            for content_ex in content_exercises:
                ex_slug = content_ex["slug"]
                content_test_cases = content_ex.get("test_cases", [])

                # Find exercise in DB by slug
                result = await session.execute(
                    select(Exercise).where(Exercise.slug == ex_slug)
                )
                db_exercise = result.scalar_one_or_none()

                if db_exercise is None:
                    print(f"  SKIP (not in DB): {ex_slug}")
                    continue

                # Compare test_cases
                db_test_cases = db_exercise.test_cases or []
                if db_test_cases != content_test_cases:
                    # Found a difference — update
                    print(f"  UPDATE: {ex_slug} (lesson: {slug})")
                    old_expected = db_test_cases[0].get("expected_output", "N/A") if db_test_cases else "N/A"
                    new_expected = content_test_cases[0].get("expected_output", "N/A") if content_test_cases else "N/A"
                    if old_expected != new_expected:
                        print(f"    expected_output changed:")
                        print(f"      OLD: {repr(old_expected[:80])}")
                        print(f"      NEW: {repr(new_expected[:80])}")
                    db_exercise.test_cases = content_test_cases
                    update_count += 1
                else:
                    print(f"  OK (unchanged): {ex_slug}")

        await session.commit()

    await engine.dispose()
    return update_count


async def main():
    print(f"Content directory: {CONTENT_DIR}")
    print(f"Database URL: {DATABASE_URL}")
    print()

    updates = await sync()
    print(f"\n{'=' * 50}")
    print(f"Total exercises updated: {updates}")
    if updates == 0:
        print("All exercises already in sync.")
    print(f"{'=' * 50}")
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
