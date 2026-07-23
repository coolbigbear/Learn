#!/usr/bin/env python3
"""Check test cases for exercises and debug code runner."""
import urllib.request, json

token = open('/tmp/reviewer_token.txt').read().strip()
base = 'http://localhost:8081'

def api_get(path):
    req = urllib.request.Request(f'{base}{path}', headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

def api_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f'{base}{path}', data=data, 
                                 headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                                 method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# Check exercise test cases directly from the DB/exercises.json
import os
content_dir = '/home/pi2/.hermes/projects/python-tutorials/content'

# Lesson 16 Ex1 - csv-read-basic
print("=== Lesson 16 - Ex1 test cases from content file ===")
with open(os.path.join(content_dir, '16-csv-processing', 'exercises.json')) as f:
    ex16 = json.load(f)

ex1 = ex16[0]  # csv-read-basic
print(f"Title: {ex1['title']}")
print(f"Instruction: {ex1['instruction']}")
print(f"Starter code:\n{ex1['starter_code']}")
print(f"Solution code:\n{ex1['solution_code']}")
print(f"Test cases ({len(ex1['test_cases'])}):")
for i, tc in enumerate(ex1['test_cases']):
    print(f"  [{i}] input={repr(tc.get('input',''))[:100]}")
    print(f"      expected_output={repr(tc.get('expected_output',''))[:100]}")
    print(f"      comparison_type={tc.get('comparison_type')}")
print()

# Lesson 17 Ex1 - json-parse-string  
print("=== Lesson 17 - Ex1 test cases from content file ===")
with open(os.path.join(content_dir, '17-json-processing', 'exercises.json')) as f:
    ex17 = json.load(f)

ex_17_1 = ex17[0]
print(f"Test cases ({len(ex_17_1['test_cases'])}):")
for i, tc in enumerate(ex_17_1['test_cases']):
    print(f"  [{i}] input={repr(tc.get('input',''))[:100]}")
    print(f"      expected_output={repr(tc.get('expected_output',''))[:100]}")
    print(f"      comparison_type={tc.get('comparison_type')}")
print(f"Solution:\n{ex_17_1['solution_code']}")
print()

# Lesson 18 Ex1 - pandas-create-dataframe
print("=== Lesson 18 - Ex1 test cases from content file ===")
with open(os.path.join(content_dir, '18-data-processing-libraries', 'exercises.json')) as f:
    ex18 = json.load(f)

ex_18_1 = ex18[0]
print(f"Test cases ({len(ex_18_1['test_cases'])}):")
for i, tc in enumerate(ex_18_1['test_cases']):
    print(f"  [{i}] input={repr(tc.get('input',''))[:100]}")
    print(f"      expected_output={repr(tc.get('expected_output',''))[:100]}")
    print(f"      comparison_type={tc.get('comparison_type')}")
print(f"Solution:\n{ex_18_1['solution_code']}")
print()

# Try just running the solution code directly in a subprocess
import subprocess
result = subprocess.run(['python3', '-c', ex1['solution_code']], capture_output=True, text=True, timeout=5)
print("=== Running solution directly ===")
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
