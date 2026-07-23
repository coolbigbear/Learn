#!/usr/bin/env python3
"""Seed database with lessons and exercises from content/ directory.

Usage:
    cd /opt/data/projects/python-tutorials/api
    python ../scripts/seed_db.py

Reads content/manifest.json for lesson ordering, then each lesson's
lesson.md and exercises.json to populate the database.
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure the api directory is on the path
api_dir = Path(__file__).resolve().parent.parent / "api"
sys.path.insert(0, str(api_dir))

# --- Database setup ---
# We need to set up an engine and session to use the models
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.database import Base
from app.models import Lesson, Exercise

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
DATABASE_URL = "sqlite+aiosqlite:///./tutorials.db"


async def ensure_path_column(engine):
    """Add the `path` column to the lessons table if it doesn't exist."""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(lessons)"))
        columns = {row.name for row in result.fetchall()}
        if "path" not in columns:
            await conn.execute(
                text("ALTER TABLE lessons ADD COLUMN path VARCHAR(50) NOT NULL DEFAULT 'python'")
            )
            await conn.commit()
            print("Added `path` column to lessons table")
        else:
            print("`path` column already exists")


async def update_existing_lessons(session, manifest):
    """Update existing lessons with their path from the manifest."""
    for entry in manifest:
        slug = entry["slug"]
        expected_path = entry.get("path", "python")
        result = await session.execute(
            select(Lesson).where(Lesson.slug == slug)
        )
        lesson = result.scalar_one_or_none()
        if lesson is not None and lesson.path != expected_path:
            lesson.path = expected_path
            print(f"  Updated path for {slug}: {expected_path} (was: {lesson.path})")

    await session.commit()


async def seed():
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure the path column exists (migration for existing databases)
    await ensure_path_column(engine)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        # Read manifest — supports both flat and language-nested layouts
        manifest_path = CONTENT_DIR / "manifest.json"
        if not manifest_path.exists():
            if CONTENT_DIR.is_dir():
                for sub in sorted(CONTENT_DIR.iterdir()):
                    if sub.is_dir():
                        candidate = sub / "manifest.json"
                        if candidate.exists():
                            manifest_path = candidate
                            break
        if not manifest_path.exists():
            print(f"ERROR: manifest not found in {CONTENT_DIR}")
            return

        with open(manifest_path) as f:
            manifest = json.load(f)

        print(f"Found {len(manifest)} lessons in manifest")

        # Check if data already exists
        result = await session.execute(select(Lesson).limit(1))
        existing = result.scalar_one_or_none()
        if existing is not None:
            print("Database already has lessons. Updating existing records...")
            await update_existing_lessons(session, manifest)
            print("Migration complete!")
            await engine.dispose()
            return

        for entry in manifest:
            slug = entry["slug"]
            path_key = entry.get("path", "python")
            lesson_dir = CONTENT_DIR / path_key / slug

            # Read lesson.md
            md_path = lesson_dir / "lesson.md"
            if not md_path.exists():
                print(f"  WARNING: {md_path} not found, skipping")
                continue

            content = md_path.read_text()

            lesson = Lesson(
                slug=slug,
                title=entry["title"],
                content=content,
                path=entry.get("path", "python"),
                order=entry["order"],
            )
            session.add(lesson)
            await session.flush()  # get lesson.id
            print(f"  Added lesson: {slug}")

            # Read exercises.json
            ex_path = lesson_dir / "exercises.json"
            if not ex_path.exists():
                print(f"  WARNING: {ex_path} not found, no exercises for {slug}")
                continue

            with open(ex_path) as f:
                exercises_data = json.load(f)

            for i, ex_data in enumerate(exercises_data):
                exercise = Exercise(
                    lesson_id=lesson.id,
                    slug=ex_data.get("slug", f"{slug}-ex-{i + 1}"),
                    title=ex_data.get("title", f"Exercise {i + 1}"),
                    instruction=ex_data.get("instruction", ""),
                    starter_code=ex_data.get("starter_code", "# Write your code here\n"),
                    solution_code=ex_data.get("solution_code", ""),
                    test_cases=ex_data.get("test_cases", []),
                    order=ex_data.get("order", i + 1),
                )
                session.add(exercise)
                print(f"    Added exercise: {exercise.slug}")

        await session.commit()
        print("\nSeed complete!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
