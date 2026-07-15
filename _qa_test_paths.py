#!/usr/bin/env python3
"""Quick QA script for learning path split verification."""
import urllib.request
import json
import sys

BASE = "https://pi2.tail8c7cb.ts.net"
TOKEN = "ab096c90d0614e72ba29cbc18805dfe2bdfbccc51b634d19"

def api(path):
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

print("=" * 60)
print("1. /api/lessons — path field verification")
print("=" * 60)
data = api("/api/lessons")
lessons = data if isinstance(data, list) else data.get("lessons", data.get("data", []))
print(f"Total lessons: {len(lessons)}")

no_path = [l for l in lessons if "path" not in l or l.get("path") is None]
print(f"Lessons without path: {len(no_path)}")
if no_path:
    for l in no_path:
        print(f"  #{l.get('id')} '{l.get('title','')}' has no path")

paths = {}
for l in lessons:
    p = l.get("path", "MISSING")
    paths.setdefault(p, []).append(l["id"])

for p in sorted(paths.keys()):
    ids = paths[p]
    print(f"  path={p}: lesson ids {ids}")

print()
print("=" * 60)
print("2. /api/lessons/by-path — grouped endpoint")
print("=" * 60)
bypath = api("/api/lessons/by-path")
if "error" in bypath:
    print(f"ERROR: {bypath['error']}")
else:
    print(json.dumps(bypath, indent=2)[:2000])

print()
print("=" * 60)
print("3. Verification against spec")
print("=" * 60)
errors = []

# Check core (lessons 1-15)
core_ids = paths.get("core", [])
expected_core = list(range(1, 16))
if sorted(core_ids) == expected_core:
    print("  ✓ core path has lessons 1-15")
else:
    errors.append(f"core: got {core_ids}, expected {expected_core}")

# Check data-processing (lesson 16)
dp_ids = paths.get("data-processing", [])
if 16 in dp_ids:
    print("  ✓ data-processing path has lesson 16")
else:
    errors.append(f"data-processing: got {dp_ids}, expected [16]")

# Check api (lessons 17-18)
api_ids = paths.get("api", [])
if sorted(api_ids) == [17, 18]:
    print("  ✓ api path has lessons 17-18")
else:
    errors.append(f"api: got {api_ids}, expected [17, 18]")

# Check machine-learning exists (even if empty)
if "machine-learning" in paths:
    print(f"  ✓ machine-learning path exists with lessons: {paths['machine-learning']}")
else:
    errors.append("machine-learning path missing from /api/lessons")

if errors:
    print(f"\n  ❌ ERRORS FOUND:")
    for e in errors:
        print(f"     {e}")
    sys.exit(1)
else:
    print(f"\n  ✅ All path checks pass!")
