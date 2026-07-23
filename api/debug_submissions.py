"""Debug exercise submissions."""
import json, urllib.request, sys

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

def api_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f'{base}{path}', data=data,
                                 headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                                 method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# Test 1: CSV Ex1 (id=60)
print("=== Test 1: CSV Ex1 (id=60) ===")
r = api_post('/api/exercises/60/submit', {
    'code': 'import csv\nimport io\ndata = """name,age,city\nAlice,25,New York\nBob,30,London\nCharlie,35,Tokyo"""\nreader = csv.reader(io.StringIO(data))\nnext(reader)\nfor row in reader:\n    print(row)',
    'language': 'python'
})
print(f'  passed={r["passed"]}, errors={r.get("errors")}')
print(f'  actual={repr(r.get("actual_output",""))[:120]}')
print(f'  expected={repr(r.get("expected_output",""))[:120]}')
if r.get('test_results'):
    tr = r['test_results'][0]
    print(f'  sub: passed={tr["passed"]}, err={tr.get("errors")}, msg={tr.get("message","")[:80]}')

# Test 5: FastAPI Ex1 (id=88)
print("\n=== Test 5: FastAPI Ex1 (id=88) ===")
r = api_post('/api/exercises/88/submit', {
    'code': 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\nasync def root():\n    return {"message": "Hello, FastAPI!"}',
    'language': 'python'
})
print(f'  passed={r["passed"]}, errors={r.get("errors")}')
print(f'  actual={repr(r.get("actual_output",""))[:120]}')
print(f'  expected={repr(r.get("expected_output",""))[:120]}')
if r.get('test_results'):
    for tr in r['test_results'][:2]:
        print(f'  sub: passed={tr["passed"]}, err={tr.get("errors")}, msg={tr.get("message","")[:80]}')

# Test 6: Mini API Project Ex1 (id=91)
print("\n=== Test 6: Mini API Ex1 (id=91) ===")
r = api_post('/api/exercises/91/submit', {
    'code': 'from fastapi import FastAPI\n\napp = FastAPI()\nitems = ["Learn Python", "Build API"]\n\n@app.get("/items")\nasync def list_items():\n    return {"items": items}',
    'language': 'python'
})
print(f'  passed={r["passed"]}, errors={r.get("errors")}')
print(f'  actual={repr(r.get("actual_output",""))[:120]}')
print(f'  expected={repr(r.get("expected_output",""))[:120]}')

# Test 3: JSON Ex1 (id=70)
print("\n=== Test 3: JSON Ex1 (id=70) ===")
r = api_post('/api/exercises/70/submit', {
    'code': 'import json\ndata = \'{"name": "Alice", "age": 25, "city": "New York"}\'\nparsed = json.loads(data)\nprint(parsed["name"])',
    'language': 'python'
})
print(f'  passed={r["passed"]}, errors={r.get("errors")}')
print(f'  actual={repr(r.get("actual_output",""))[:120]}')
print(f'  expected={repr(r.get("expected_output",""))[:120]}')

# Test 4: Pandas Ex1 (id=80)
print("\n=== Test 4: Pandas Ex1 (id=80) ===")
r = api_post('/api/exercises/80/submit', {
    'code': 'import pandas as pd\ndf = pd.DataFrame({\n    \'name\': [\'Alice\', \'Bob\', \'Charlie\'],\n    \'age\': [25, 30, 35],\n    \'city\': [\'New York\', \'London\', \'Tokyo\']\n})\nprint(df)',
    'language': 'python'
})
print(f'  passed={r["passed"]}, errors={r.get("errors")}')
print(f'  actual={repr(r.get("actual_output",""))[:120]}')
print(f'  expected={repr(r.get("expected_output",""))[:120]}')

# Test 2: CSV Ex1 starter should FAIL
print("\n=== Test 2: CSV Ex1 starter (should FAIL) ===")
r = api_post('/api/exercises/60/submit', {
    'code': 'import csv\nimport io\n\ndata = """name,age,city\nAlice,25,New York\nBob,30,London\nCharlie,35,Tokyo"""\n\n# Create reader and print each row\n',
    'language': 'python'
})
print(f'  passed={r["passed"]}, errors={r.get("errors")}')
print(f'  actual={repr(r.get("actual_output",""))[:120]}')
