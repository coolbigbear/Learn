import json
import urllib.request
import sys

BASE = "http://localhost:8081"

# 1. Login
req = urllib.request.Request(
    f"{BASE}/api/auth/login",
    data=json.dumps({"username": "reviewer", "password": "devprofile"}).encode(),
    headers={"Content-Type": "application/json"},
)
resp = urllib.request.urlopen(req)
auth = json.loads(resp.read())
token = auth["token"]

# 2. Get exercise 100
req = urllib.request.Request(
    f"{BASE}/api/exercises/100",
    headers={"Authorization": f"Bearer {token}"},
)
resp = urllib.request.urlopen(req)
ex = json.loads(resp.read())
print(f"Exercise: {ex['slug']} - {ex['title']}")

# 3. Run with correct solution
code = (
    "import numpy as np\n"
    "np.random.seed(42)\n"
    "data = np.random.rand(10)\n"
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

expected = result["expected_output"]
actual = result["actual_output"]

errors = []
if not result["passed"]:
    errors.append(f"FAILED: passed={result['passed']}")
if "0.5201" not in expected:
    errors.append(f"Expected output missing numpy 2.x mean (0.5201): {expected!r}")
if "0.0581" not in expected:
    errors.append(f"Expected output missing numpy 2.x min (0.0581): {expected!r}")
if actual != expected:
    errors.append(f"Output mismatch:\n  Expected: {expected!r}\n  Actual:   {actual!r}")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
else:
    print("PASS: Exercise 100 runs and matches exactly")
    print(f"  Expected == Actual == {expected!r}")
    sys.exit(0)
