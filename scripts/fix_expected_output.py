#!/usr/bin/env python3
"""
Fix DB expected_output mismatch for exercise random-data (ex-21-7, id=100).

The content file was updated with correct numpy 2.x values, but the Docker
image was built before the fix, so the baked-in /app/content/ still has stale
values and the sync function never detects a difference.

This script:
  - Reads the content file directly (host copy, which has correct values)
  - Updates the exercise test_cases in the DB inside the Docker container

Usage:
  python scripts/fix_expected_output.py [container_name]
  Default container: python-tutorials-qa
"""
import json
import subprocess
import sys
from pathlib import Path

CONTENT_FILE = Path(__file__).resolve().parent.parent / "content" / "python" / "24-intro-to-ml" / "exercises.json"
EXERCISE_SLUG = "random-data"


def get_container_db_path(container: str) -> str:
    """Find the SQLite DB path inside the container."""
    result = subprocess.run(
        ["docker", "exec", container, "sh", "-c",
         "ls /app/data/tutorials.db 2>/dev/null || ls /app/tutorials.db 2>/dev/null || echo 'NOT FOUND'"],
        capture_output=True, text=True, timeout=10,
    )
    return result.stdout.strip()


def get_current_db_test_cases(container: str, db_path: str) -> list:
    """Read the current test_cases from the DB inside the container."""
    result = subprocess.run(
        ["docker", "exec", container, "sqlite3", db_path,
         f"SELECT test_cases FROM exercises WHERE slug='{EXERCISE_SLUG}'"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0 or not result.stdout.strip():
        print(f"ERROR: Could not read exercise '{EXERCISE_SLUG}' from DB")
        print(f"  stderr: {result.stderr}")
        return None
    return json.loads(result.stdout.strip())


def update_db_test_cases(container: str, db_path: str, new_test_cases_json: str) -> bool:
    """Update the exercise test_cases in the DB."""
    # Escape single quotes by doubling them (SQLite escape)
    escaped = new_test_cases_json.replace("'", "''")
    result = subprocess.run(
        ["docker", "exec", container, "sqlite3", db_path,
         f"UPDATE exercises SET test_cases = '{escaped}' WHERE slug = '{EXERCISE_SLUG}'"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"ERROR: Update failed: {result.stderr}")
        return False
    return True


def main():
    container = sys.argv[1] if len(sys.argv) > 1 else "python-tutorials-qa"

    # 1. Read the correct expected_output from the content file
    if not CONTENT_FILE.exists():
        print(f"ERROR: Content file not found: {CONTENT_FILE}")
        sys.exit(1)

    with open(CONTENT_FILE) as f:
        exercises = json.load(f)

    target_ex = None
    for ex in exercises:
        if ex["slug"] == EXERCISE_SLUG:
            target_ex = ex
            break

    if target_ex is None:
        print(f"ERROR: Exercise '{EXERCISE_SLUG}' not found in content file")
        sys.exit(1)

    correct_test_cases = target_ex.get("test_cases", [])
    correct_expected = correct_test_cases[0]["expected_output"]
    print(f"Correct expected_output from content file:")
    print(repr(correct_expected))

    # 2. Check current DB state
    db_path = get_container_db_path(container)
    print(f"\nContainer: {container}")
    print(f"DB path: {db_path}")

    current_tc = get_current_db_test_cases(container, db_path)
    if current_tc is None:
        sys.exit(1)

    current_expected = current_tc[0]["expected_output"]
    print(f"\nCurrent DB expected_output:")
    print(repr(current_expected))

    if current_expected == correct_expected:
        print("\n✓ DB already matches content file. No update needed.")
        return

    # 3. Update the DB
    print(f"\n→ Updating DB...")
    new_json = json.dumps(correct_test_cases)
    if update_db_test_cases(container, db_path, new_json):
        print("✓ DB updated successfully")

    # 4. Verify
    verify_tc = get_current_db_test_cases(container, db_path)
    verify_expected = verify_tc[0]["expected_output"]
    if verify_expected == correct_expected:
        print("✓ Verification passed — DB now matches content file")
    else:
        print(f"✗ Verification FAILED")
        print(f"  Expected: {repr(correct_expected)}")
        print(f"  Got:      {repr(verify_expected)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
