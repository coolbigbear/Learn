#!/usr/bin/env python3
"""Verify lesson headings on the live QA site via the API."""
import requests

BASE = "https://pi2.tail8c7cb.ts.net"
CREDS = {"username": "content", "password": "devprofile"}

# Login
r = requests.post(f"{BASE}/api/auth/login", json=CREDS)
print("Login status:", r.status_code)
print("Login response:", r.text[:500])

if r.status_code != 200:
    print("Login failed, exiting")
    exit(1)

data = r.json()
token = data.get("access_token") or data.get("token")
if not token:
    print("No token found in response keys:", list(data.keys()))
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Check lesson 19
r = requests.get(f"{BASE}/api/lessons/19-fastapi-intro", headers=headers)
print(f"\nLesson 19 status: {r.status_code}")
data = r.json()
first_line = data.get("content", "").split("\n")[0]
print(f"  Heading: {first_line}")
if "Lesson 19" in first_line:
    print("  ✓ Correct")
else:
    print(f"  ✗ WRONG — expected Lesson 19")

# Check lesson 20
r = requests.get(f"{BASE}/api/lessons/20-mini-api-project", headers=headers)
print(f"\nLesson 20 status: {r.status_code}")
data = r.json()
first_line = data.get("content", "").split("\n")[0]
print(f"  Heading: {first_line}")
if "Lesson 20" in first_line:
    print("  ✓ Correct")
else:
    print(f"  ✗ WRONG — expected Lesson 20")
