#!/usr/bin/env python3
"""Test the exercise endpoint to verify the fix."""
import json
import subprocess
import sys
import urllib.request

BASE = "http://localhost:8081"

# Login
req = urllib.request.Request(
    f"{BASE}/api/auth/login",
    data=json.dumps({"username": "reviewer", "password": "devprofile"}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req)
auth_data = json.loads(resp.read())
token = auth_data["token"]
print(f"Logged in as reviewer, token acquired ({len(token)} chars)")

# Run exercise 100
code = (
    'import numpy as np\n'
    'np.random.seed(42)\n'
    'data = np.random.rand(10)\n'
    'print(f"Mean: {np.mean(data):.4f}")\n'
    'print(f"Max: {np.max(data):.4f}")\n'
    'print(f"Min: {np.min(data):.4f}")\n'
    'print(f"Std: {np.std(data):.4f}")\n'
)

req = urllib.request.Request(
    f"{BASE}/api/exercises/100/run",
    data=json.dumps({"code": code}).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    },
)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())

print(f"\nExercise 100 run result:")
print(f"  passed: {result.get('passed')}")
print(f"  expected_output: {repr(result.get('expected_output', ''))}")
print(f"  actual_output:   {repr(result.get('actual_output', ''))}")
print(f"  errors: {result.get('errors')}")

if result.get("passed"):
    expected = result.get("expected_output", "")
    if "0.5201" in expected and "0.0581" in expected:
        print("\n✓ FIX VERIFIED: expected_output contains numpy 2.x values, test passes!")
        sys.exit(0)
    else:
        print("\n! PASSED but unexpected expected_output value")
        sys.exit(1)
else:
    print("\n✗ FAILED: expected_output still stale or actual doesn't match")
    print(f"  Debug - actual has 0.5201? {'0.5201' in result.get('actual_output', '')}")
    print(f"  Debug - expected has 0.5201? {'0.5201' in result.get('expected_output', '')}")
    sys.exit(1)
