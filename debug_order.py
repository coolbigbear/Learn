"""Test order independence."""
import json, urllib.request

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

def api_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f'{base}{path}', data=data,
                                 headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                                 method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

code5 = 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\nasync def root():\n    return {"message": "Hello, FastAPI!"}'
code6 = 'from fastapi import FastAPI\n\napp = FastAPI()\nitems = ["Learn Python", "Build API"]\n\n@app.get("/items")\nasync def list_items():\n    return {"items": items}'

# Run individually first
print("=== Run 1: Just test 5 ===")
r = api_post('/api/exercises/88/submit', {'code': code5, 'language': 'python'})
print(f"  passed={r['passed']}, errors={r.get('errors')}")

print("=== Run 2: Just test 6 ===")
r = api_post('/api/exercises/91/submit', {'code': code6, 'language': 'python'})
print(f"  passed={r['passed']}, errors={r.get('errors')}")

# Run reverse order
print("=== Run 3: 6 then 5 ===")
r6 = api_post('/api/exercises/91/submit', {'code': code6, 'language': 'python'})
print(f"  Test 6: passed={r6['passed']}, errors={r6.get('errors')}")
r5 = api_post('/api/exercises/88/submit', {'code': code5, 'language': 'python'})
print(f"  Test 5: passed={r5['passed']}, errors={r5.get('errors')}")

# Run them multiple times to see pattern
print("\n=== Run 4-8: Alternating ===")
for i in range(5):
    r = api_post('/api/exercises/88/submit', {'code': code5, 'language': 'python'})
    r2 = api_post('/api/exercises/91/submit', {'code': code6, 'language': 'python'})
    print(f"  Run {i}: 88={r['passed']} 91={r2['passed']}")
