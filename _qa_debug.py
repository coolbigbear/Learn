#!/usr/bin/env python3
"""Dump raw API response to debug missing path fields."""
import urllib.request
import urllib.error
import json
import sys

BASE = "https://pi2.tail8c7cb.ts.net"
TOKEN = "ab096c90d0614e72ba29cbc18805dfe2bdfbccc51b634d19"

def api(path):
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            print(f"HTTP {r.status} {path}")
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {path}: {e.reason}")
        return None
    except Exception as e:
        print(f"ERROR {path}: {e}")
        return None

# Raw dump of /api/lessons
data = api("/api/lessons")
if data:
    # Determine if it's a list or wrapped
    lessons = data if isinstance(data, list) else data.get("lessons", data.get("data", []))
    print(f"\nTotal lessons: {len(lessons)}")
    print(f"First lesson raw keys: {list(lessons[0].keys()) if lessons else 'N/A'}")
    print(f"First lesson: {json.dumps(lessons[0], indent=2)}")
    print(f"Last lesson: {json.dumps(lessons[-1], indent=2)}")

# Try /api/lessons/by-path
data2 = api("/api/lessons/by-path")
if data2:
    print(f"\n/by-path response:")
    print(json.dumps(data2, indent=2)[:2000])
else:
    print("\n/by-path returned None")