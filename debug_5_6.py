"""Debug the difference between Test 5 and Test 6."""
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

# Test 5: FastAPI Ex1
print("=== FastAPI Ex1 (id=88) ===")
code5 = 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\nasync def root():\n    return {"message": "Hello, FastAPI!"}'
print(f"  code length: {len(code5)}")
print(f"  code repr: {repr(code5)[:150]}")
r = api_post('/api/exercises/88/submit', {'code': code5, 'language': 'python'})
print(f"  passed={r['passed']}")
print(f"  errors={r.get('errors')}")
print(f"  actual={repr(r.get('actual_output',''))[:120]}")
print(f"  test_results: {json.dumps(r.get('test_results', []), indent=2)[:300]}")

# Test 6: Mini API Ex1
print("\n=== Mini API Ex1 (id=91) ===")
code6 = 'from fastapi import FastAPI\n\napp = FastAPI()\nitems = ["Learn Python", "Build API"]\n\n@app.get("/items")\nasync def list_items():\n    return {"items": items}'
print(f"  code length: {len(code6)}")
print(f"  code repr: {repr(code6)[:150]}")
r = api_post('/api/exercises/91/submit', {'code': code6, 'language': 'python'})
print(f"  passed={r['passed']}")
print(f"  errors={r.get('errors')}")
print(f"  actual={repr(r.get('actual_output',''))[:120]}")
print(f"  test_results: {json.dumps(r.get('test_results', []), indent=2)[:300]}")
