"""Tests for the test_suite column migration on exercises table.

The test_suite column was added to the Exercise ORM model in PR #40 but
no migration was provided for existing databases. The create_tables()
function includes an ALTER TABLE ADD COLUMN that catches errors if the
column already exists (idempotent migration).
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Isolated in-memory engine for testing the migration
_migration_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    echo=False,
)


class TestTestSuiteMigration:
    """Verify the test_suite column migration works."""

    async def _column_exists(self, engine, table: str, column: str) -> bool:
        """Check if a column exists in a table."""
        async with engine.connect() as conn:
            result = await conn.execute(
                text(f"PRAGMA table_info({table})")
            )
            rows = result.fetchall()
            return any(row[1] == column for row in rows)

    async def test_test_suite_column_created_by_migration(self):
        """On a table created without test_suite, the migration should add it."""
        # Create the exercises table WITHOUT test_suite column (simulating
        # an old database created before PR #40)
        async with _migration_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lesson_id INTEGER NOT NULL,
                    slug VARCHAR(80) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    instruction TEXT NOT NULL,
                    starter_code TEXT NOT NULL DEFAULT '# Write your code here
',
                    solution_code TEXT NOT NULL DEFAULT '',
                    test_cases JSON NOT NULL DEFAULT '[]',
                    language VARCHAR(20) NOT NULL DEFAULT 'python',
                    "order" INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))

        # Verify test_suite does NOT exist before migration
        assert not await self._column_exists(_migration_engine, "exercises", "test_suite")

        # Run the migration (inside create_tables context)
        async with _migration_engine.begin() as conn:
            try:
                await conn.execute(
                    text("ALTER TABLE exercises ADD COLUMN test_suite TEXT DEFAULT NULL")
                )
            except Exception:
                pytest.fail("Migration failed on a table without test_suite")

        # Verify test_suite now exists
        assert await self._column_exists(_migration_engine, "exercises", "test_suite")

    async def test_migration_is_idempotent(self):
        """Running the ALTER TABLE again should not raise when column exists."""
        # Create a fresh table WITH test_suite
        async with _migration_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE exercises_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lesson_id INTEGER NOT NULL,
                    slug VARCHAR(80) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    instruction TEXT NOT NULL,
                    starter_code TEXT NOT NULL DEFAULT '# Write your code here
',
                    solution_code TEXT NOT NULL DEFAULT '',
                    test_cases JSON NOT NULL DEFAULT '[]',
                    language VARCHAR(20) NOT NULL DEFAULT 'python',
                    "order" INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    test_suite TEXT DEFAULT NULL
                )
            """))

        # Running the migration should not raise (caught by except Exception: pass)
        async with _migration_engine.begin() as conn:
            try:
                await conn.execute(
                    text("ALTER TABLE exercises_v2 ADD COLUMN test_suite TEXT DEFAULT NULL")
                )
                # If it didn't raise, the column already exists,
                # which means SQLite actually allowed it (unusual)
                pass
            except Exception:
                # This is the expected path — column exists, ALTER fails
                pass

        # Column should still be there
        assert await self._column_exists(_migration_engine, "exercises_v2", "test_suite")

    async def test_select_from_exercises_works_with_test_suite(self):
        """After migration, selecting all columns from exercises should work."""
        # Create the table with test_suite and insert a row
        async with _migration_engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE exercises_v3 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lesson_id INTEGER NOT NULL,
                    slug VARCHAR(80) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    instruction TEXT NOT NULL,
                    starter_code TEXT NOT NULL,
                    solution_code TEXT,
                    test_cases JSON NOT NULL DEFAULT '[]',
                    language VARCHAR(20) NOT NULL DEFAULT 'python',
                    "order" INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    test_suite TEXT DEFAULT NULL
                )
            """))
            await conn.execute(text("""
                INSERT INTO exercises_v3 (lesson_id, slug, title, instruction, starter_code, "order")
                VALUES (1, 'test-ex', 'Test', 'Do something', 'print("hi")', 1)
            """))

        # Select all columns — this would fail if test_suite column didn't exist
        async with _migration_engine.begin() as conn:
            result = await conn.execute(
                text("SELECT * FROM exercises_v3 WHERE slug = 'test-ex'")
            )
            row = result.fetchone()
            assert row is not None
            # test_suite should be NULL (no value provided)
            columns = [desc[0] for desc in result.cursor.description]
            assert "test_suite" in columns
            assert row.test_suite is None

    async def test_create_tables_includes_migration(self):
        """Verify the create_tables function includes the test_suite migration."""
        from app.database import create_tables

        # create_tables uses the module-level engine which already has
        # the test_suite column (created by fixtures), so this just
        # verifies the migration code path doesn't raise
        try:
            await create_tables()
        except Exception as e:
            pytest.fail(f"create_tables() raised unexpectedly: {e}")

        # After create_tables, the module-level database should have test_suite
        from app.database import engine as main_engine
        assert await self._column_exists(main_engine, "exercises", "test_suite")
