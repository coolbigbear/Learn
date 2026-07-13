import urllib.request, json, sys

def test_endpoint(name, url, method="GET", data=None, headers=None):
    hdrs = headers or {}
    if data is not None:
        hdrs["Content-Type"] = "application/json"
        data_bytes = json.dumps(data).encode()
    else:
        data_bytes = None
    req = urllib.request.Request(url, data=data_bytes, headers=hdrs, method=method)
    try:
        resp = urllib.request.urlopen(req)
        body = json.loads(resp.read())
        print(f"[PASS] {name}: {resp.status}")
        return body
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:200]
        print(f"[FAIL] {name}: {e.code} - {err}")
        return None

BASE = "https://influences-auction-mature-colon.trycloudflare.com"

# Health check
test_endpoint("Health", f"{BASE}/api/health")

# Register
reg = test_endpoint("Register", f"{BASE}/api/auth/register", method="POST",
                     data={"username": "qatest_x99", "password": "TestPass123!"})
if not reg:
    print("Cannot proceed without auth token")
    sys.exit(1)

token = reg["token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"  token={token[:20]}...")

# Run exercise
run = test_endpoint("Run Exercise 1", f"{BASE}/api/exercises/1/run", method="POST",
                     data={"code": 'print("Hello from API test!")'}, headers=headers)
if run:
    print(f"  output={run.get('actual_output', 'N/A')}")
    print(f"  errors={run.get('errors', 'N/A')}")
    print(f"  passed={run.get('passed', 'N/A')}")

# Submit exercise
sub = test_endpoint("Submit Exercise 1", f"{BASE}/api/exercises/1/submit", method="POST",
                     data={"code": 'print("Hello from API test!")'}, headers=headers)
if sub:
    print(f"  output={sub.get('actual_output', 'N/A')}")
    print(f"  errors={sub.get('errors', 'N/A')}")
    print(f"  passed={sub.get('passed', 'N/A')}")

# Progress
prog = test_endpoint("Progress", f"{BASE}/api/progress", headers=headers)
if prog:
    print(f"  {json.dumps(prog, indent=2)}")

# Login
login = test_endpoint("Login", f"{BASE}/api/auth/login", method="POST",
                       data={"username": "qatest_x99", "password": "TestPass123!"})
if login:
    print(f"  token={login['token'][:20]}...")

# Test staging too
BASE2 = "https://anniversary-consciousness-examination-consulting.trycloudflare.com"
print("\n--- Staging ---")
test_endpoint("Staging Health", f"{BASE2}/api/health")
test_endpoint("Staging Register", f"{BASE2}/api/auth/register", method="POST",
               data={"username": "qatest_stg1", "password": "TestPass123!"})