"""Fix lesson headings in the persistent QA database.

Updates lesson content for slugs '19-fastapi-intro' and '20-mini-api-project'
by replacing the wrong heading numbers (Lesson 17 / Lesson 18) with the correct
ones (Lesson 19 / Lesson 20) directly in the SQLite database.
"""
import asyncio
import sqlite3
from pathlib import Path


DB_PATH = Path("/app/data/tutorials.db")

# Map slug → (old_heading, new_heading)
FIXES = {
    "19-fastapi-intro": (
        "# Lesson 17: Introduction to FastAPI",
        "# Lesson 19: Introduction to FastAPI",
    ),
    "20-mini-api-project": (
        "# Lesson 18: Mini API Project",
        "# Lesson 20: Mini API Project",
    ),
}


def fix_content(db_path: str) -> list[str]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = []
    for slug, (old, new) in FIXES.items():
        cursor.execute("SELECT id, slug, title, content FROM lessons WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        if not row:
            results.append(f"❌ No lesson found for slug '{slug}'")
            continue

        content = row["content"]
        if old not in content:
            results.append(f"⚠️  Slug '{slug}' — heading '{old}' not found in content. Current content starts with: {content[:80]!r}")
            continue

        updated = content.replace(old, new, 1)
        cursor.execute("UPDATE lessons SET content = ? WHERE id = ?", (updated, row["id"]))
        results.append(f"✅ Slug '{slug}' (id={row['id']}): fixed '{old}' → '{new}'")

    conn.commit()
    conn.close()
    return results


def verify(db_path: str) -> list[str]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = []
    for slug in FIXES:
        cursor.execute("SELECT slug, substr(content, 1, 80) AS start FROM lessons WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        if row:
            results.append(f"  {row['slug']}: {row['start']}")
        else:
            results.append(f"  {slug}: ❌ NOT FOUND")
    conn.close()
    return results


if __name__ == "__main__":
    db = str(DB_PATH)
    if not Path(db).exists():
        print(f"DB not found at {db}")
        # Try alternative: find it under Docker volumes
        candidates = list(Path("/var/lib/docker/volumes").rglob("tutorials.db"))
        if candidates:
            db = str(candidates[0])
            print(f"Found DB at {db}")
        else:
            print("No DB found anywhere.")
            exit(1)

    print("=== Before ===")
    for line in verify(db):
        print(line)

    print("\n=== Applying fixes ===")
    for line in fix_content(db):
        print(line)

    print("\n=== After ===")
    for line in verify(db):
        print(line)
