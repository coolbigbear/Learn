#!/usr/bin/env python3
"""Functional test: submit code for exercises and verify results.

Uses the exact solution code and test cases from exercises.json files
so the test actually validates real exercise behavior.
"""
import urllib.request, json

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

def api_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f'{base}{path}', data=data, 
                                 headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                                 method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def check_test(label, exercise_id, solution_code, expect_pass=True):
    print(f"=== {label} === (expect {'PASS' if expect_pass else 'FAIL'})")
    result = api_post(f'/api/exercises/{exercise_id}/submit', {'code': solution_code, 'language': 'python'})
    status = "PASS" if result['passed'] else "FAIL"
    icon = "✅" if result['passed'] == expect_pass else "❌"
    print(f"  {icon} passed={result['passed']} (expected {expect_pass})")
    if result.get('errors'):
        print(f"  Error: {result['errors']}")
    if result.get('test_results'):
        for tr in result['test_results']:
            msg = tr.get('message') or ''
            err = tr.get('errors') or ''
            if not tr['passed']:
                print(f"  ├─ Sub-test: passed={tr['passed']}, err={err}, msg={msg[:80]}")
    print()

# Test 1: CSV Processing - Exercise 1 (csv-read-basic, id=60)
# Solution from exercises.json — does NOT skip header, matches DB test case
solution_1 = """import csv
import io

data = \"\"\"name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo
\"\"\"

f = io.StringIO(data)
reader = csv.reader(f)
for row in reader:
    print(row)
"""
check_test("CSV Processing Ex1 - solution from exercises.json", 60, solution_1, expect_pass=True)

# Test 2: Starter code for CSV Ex1 — should FAIL (just comments, no meaningful output)
starter_code = "import csv\\nimport io\\n\\ndata = \\\"\\\"\\\"name,age,city\\nAlice,25,New York\\nBob,30,London\\nCharlie,35,Tokyo\\\"\\\"\\\"\\n\\n# Create reader and print each row\\n"
result2 = api_post('/api/exercises/60/submit', {'code': starter_code, 'language': 'python'})
print(f"=== CSV Processing Ex1 - starter code should FAIL ===")
print(f"  {'✅' if not result2['passed'] else '❌'} passed={result2['passed']} (expected False)")
if result2.get('test_results'):
    for tr in result2['test_results']:
        print(f"  Test: passed={tr.get('passed')}, err={tr.get('errors')}, msg={tr.get('message','')[:60]}")
print()

# Test 3: JSON Processing - Exercise 1 (json-parse-string, id=70)
# Solution from exercises.json — prints parsed["city"] which is "Paris"
solution_3 = """import json

data = '{\"name\": \"Alice\", \"age\": 25, \"city\": \"Paris\"}'
parsed = json.loads(data)
print(parsed[\"city\"])
"""
check_test("JSON Processing Ex1 - solution from exercises.json", 70, solution_3, expect_pass=True)

# Test 4: Data Processing Libraries - Exercise 1 (pandas-create-dataframe, id=80)
# Solution from exercises.json
solution_4 = """import pandas as pd

data = {
    \"name\": [\"Alice\", \"Bob\", \"Charlie\"],
    \"age\": [25, 30, 35],
    \"score\": [85, 92, 78],
}

df = pd.DataFrame(data)
print(df)
"""
check_test("Data Processing Ex1 - solution from exercises.json", 80, solution_4, expect_pass=True)

# Test 5: FastAPI Intro - Exercise 1 (fastapi-hello, id=88)
# Solution from exercises.json — creates app with route but no output expected
solution_5 = """from fastapi import FastAPI

app = FastAPI()

@app.get(\"/\")
async def root():
    return {\"message\": \"Hello, FastAPI!\"}
"""
check_test("FastAPI Intro Ex1 - solution from exercises.json", 88, solution_5, expect_pass=True)

# Test 6: Mini API Project - Exercise 1 (project-create-crud, id=91)
# Solution from exercises.json
solution_6 = """from fastapi import FastAPI

app = FastAPI()
items = [\"Learn Python\", \"Build API\"]

@app.get(\"/items\")
async def list_items():
    return {\"items\": items}
"""
check_test("Mini API Project Ex1 - solution from exercises.json", 91, solution_6, expect_pass=True)

print("✅ All functional tests complete")
