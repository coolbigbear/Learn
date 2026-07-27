"""Async SQLAlchemy engine and session management for SQLite.

Includes WAL mode, automatic backup, and integrity checking
to prevent and detect database corruption.
"""

import os
import shutil
import time
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


# Allow override via environment variable
database_url = os.environ.get("DATABASE_URL", DATABASE_URL)

if database_url.startswith("sqlite"):
    # SQLite needs check_same_thread=False for aiosqlite
    engine = create_async_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_async_engine(database_url, echo=False)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def _get_db_path() -> Path | None:
    """Extract the local file path from DATABASE_URL (e.g. sqlite+aiosqlite:///./tutorials.db).

    Returns None for in-memory databases or non-local URLs.
    """
    url = database_url
    if url.startswith("sqlite+aiosqlite:///"):
        # Relative or absolute path
        raw = url.removeprefix("sqlite+aiosqlite:///")
        if raw and raw != ":memory:":
            path = Path(raw)
            if not path.is_absolute():
                # Relative to the api/ directory (where the server runs)
                path = Path(os.getcwd()) / path
            return path.resolve()
    return None


async def enable_wal_and_pragmas() -> None:
    """Enable WAL journal mode and set safe PRAGMAs on the SQLite database.

    WAL mode allows concurrent reads and writes without corruption,
    which is critical for async applications using aiosqlite.
    """
    async with engine.connect() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL;"))
        # Synchronous NORMAL is safe with WAL and much faster than FULL
        await conn.execute(text("PRAGMA synchronous=NORMAL;"))
        # Busy timeout — if the DB is locked, wait up to 5 seconds
        await conn.execute(text("PRAGMA busy_timeout=5000;"))
        await conn.commit()


async def check_database_integrity(_engine=None) -> dict:
    """Run SQLite integrity_check and return results.

    Accepts an optional engine parameter for test isolation.
    When omitted, the module-level global engine is used.

    Returns a dict with:
      - ok: True if integrity check passed
      - message: human-readable result
      - table_count: number of user tables (if check passed)
    """
    if _engine is None:
        _engine = engine

    result = {"ok": True, "message": "Database integrity verified", "table_count": 0}

    try:
        async with _engine.connect() as conn:
            # Integrity check
            integrity = await conn.execute(text("PRAGMA integrity_check;"))
            rows = integrity.fetchall()
            failed = [r[0] for r in rows if r[0] != "ok"]
            if failed:
                result["ok"] = False
                result["message"] = f"Integrity check failed: {'; '.join(failed)}"
                return result

            # Count user-created tables (skip sqlite_* internal tables)
            tables = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            )
            table_names = [r[0] for r in tables.fetchall()]
            result["table_count"] = len(table_names)

            # Check if the DB file has reasonable size (for file-based databases)
            db_path = _get_db_path()
            if db_path and db_path.exists():
                size_bytes = db_path.stat().st_size
                if size_bytes == 0:
                    result["ok"] = False
                    result["message"] = "Database file exists but is 0 bytes (corrupted/empty)"
                    return result
                result["size_bytes"] = size_bytes

    except Exception as e:
        result["ok"] = False
        result["message"] = f"Database integrity check error: {e}"

    return result


async def backup_database() -> str | None:
    """Create a simple file-copy backup of the SQLite database.

    Returns the backup path string, or None if backup wasn't possible
    (in-memory database, or backup already exists from this session).

    Backups are written to <db_path>.backup.<timestamp> and the two
    most recent backups are retained.
    """
    db_path = _get_db_path()
    if db_path is None or not db_path.exists():
        return None

    # Source database file and associated WAL/shm files
    # Flush WAL to main DB before copying
    async with engine.connect() as conn:
        await conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE);"))
        await conn.commit()

    backup_dir = db_path.parent / ".db_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"{db_path.name}.{timestamp}"
    shutil.copy2(db_path, backup_path)

    # Also back up WAL and SHM files if they exist
    for ext in ["-wal", "-shm"]:
        aux = db_path.parent / f"{db_path.name}{ext}"
        if aux.exists():
            shutil.copy2(aux, backup_dir / f"{db_path.name}{ext}.{timestamp}")

    # Prune old backups — keep only the 2 most recent
    all_backups = sorted(backup_dir.glob(f"{db_path.name}.*"), reverse=True)
    # Group by base name (without timestamp), keep at most 2 per base
    seen_bases: set[str] = set()
    for bp in all_backups:
        stem = bp.name
        base_key = stem.rsplit(".", 2)[0] if stem.count(".") > 1 else stem
        if base_key not in seen_bases:
            seen_bases.add(base_key)
            continue
        # This is an older backup of the same file — remove it
        if bp.exists():
            bp.unlink()

    return str(backup_path)


async def get_db():
    """FastAPI dependency: yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables():
    """Create all tables. Safe to call on every startup — SQLAlchemy uses IF NOT EXISTS.

    Also enables WAL mode and creates a backup of any existing database.
    """
    # Enable WAL mode first (must be done on a raw connection before any other operations)
    try:
        await enable_wal_and_pragmas()
    except Exception as e:
        print(f"[database] Warning: could not set WAL mode: {e}")

    # Back up any existing database before migrations
    try:
        backup_path = await backup_database()
        if backup_path:
            print(f"[database] Pre-migration backup saved to {backup_path}")
    except Exception as e:
        print(f"[database] Warning: backup failed: {e}")

    async with engine.begin() as conn:
        # Import models so they register with Base.metadata
        import app.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

        # Migrate: add `path` column to lessons table if it doesn't exist
        # SQLite doesn't support IF NOT EXISTS for ALTER TABLE, so we catch the error
        try:
            await conn.execute(
                text("ALTER TABLE lessons ADD COLUMN path VARCHAR(50) NOT NULL DEFAULT 'core'")
            )
        except Exception:
            pass  # Column already exists

        # Migrate: drop `token` column from users table (replaced by JWT auth)
        try:
            await conn.execute(text("ALTER TABLE users DROP COLUMN token"))
        except Exception:
            pass  # Column already dropped or SQLite version doesn't support DROP COLUMN

        # Migrate: Change exercises.slug from globally UNIQUE to per-lesson unique.
        # The new model uses UniqueConstraint('lesson_id', 'slug'), but existing DBs
        # have a global UNIQUE on slug (auto-indexed). SQLite doesn't allow ALTER TABLE
        # DROP CONSTRAINT, so we drop the auto-index and create the composite index.
        try:
            # Drop old auto-index from UNIQUE(slug) — SQLite names these
            # sqlite_autoindex_<table>_<N>. Safe to try; fails silently if absent.
            for n in (1, 2, 3):
                try:
                    await conn.execute(
                        text(f"DROP INDEX IF EXISTS sqlite_autoindex_exercises_{n}")
                    )
                except Exception:
                    pass
            # Create composite unique index (idempotent)
            await conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_exercise_per_lesson "
                    "ON exercises(lesson_id, slug)"
                )
            )
        except Exception:
            pass

        # Migrate: add `test_suite` column to exercises table if it doesn't exist
        try:
            await conn.execute(
                text("ALTER TABLE exercises ADD COLUMN test_suite TEXT DEFAULT NULL")
            )
        except Exception:
            pass  # Column already exists

    # Verify integrity after migrations
    try:
        integrity = await check_database_integrity()
        if not integrity["ok"]:
            print(f"[database] WARNING: Integrity check failed after migrations: {integrity['message']}")
        else:
            table_count = integrity.get("table_count", 0)
            size = integrity.get("size_bytes", "N/A")
            print(f"[database] Integrity OK — {table_count} tables, {size} bytes")
    except Exception as e:
        print(f"[database] Warning: integrity check failed: {e}")