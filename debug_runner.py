#!/usr/bin/env python3
"""Debug the code runner API."""
import urllib.request, json, traceback

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

def api_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f'{base}{path}', data=data, 
                                 headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                                 method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP Error {e.code}: {body[:500]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return None

# Try the RUN endpoint (not submit) for more debug info
print("=== Test: Run solution for CSV Ex1 (id=60) ===")
solution = """import csv
import io

data = \"\"\"name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo\"\"\"

f = io.StringIO(data)
reader = csv.reader(f)
for row in reader:
    print(row)
"""
result = api_post('/api/exercises/60/run', {'code': solution, 'language': 'python'})
if result:
    print(f"Full result: {json.dumps(result, indent=2)[:1000]}")

# Try with a simpler print statement
print("\n=== Test: Run simple print ===")
result2 = api_post('/api/exercises/60/run', {'code': 'print("hello world")', 'language': 'python'})
if result2:
    print(f"Full result: {json.dumps(result2, indent=2)[:500]}")
