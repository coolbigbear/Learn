#!/usr/bin/env python3
"""Check FastAPI exercise solutions for import usage."""
import json

with open('/home/pi2/.hermes/projects/python-tutorials/content/python/19-json-api-payloads/exercises.json') as f:
    ex19 = json.load(f)

with open('/home/pi2/.hermes/projects/python-tutorials/content/python/20-form-handling/exercises.json') as f:
    ex20 = json.load(f)

print("=== Lesson 19: JSON API Payloads ===")
for ex in ex19:
    print(f"\nExercise {ex['order']}: {ex['title']}")
    print(f"  Starter has import: {'import' in ex['starter_code'] or 'from' in ex['starter_code']}")
    print(f"  Solution has import: {'import' in ex['solution_code'] or 'from' in ex['solution_code']}")
    # Show first line of starter
    starter_lines = ex['starter_code'].strip().split('\n')
    print(f"  Starter first lines: {starter_lines[:3]}")
    # Show test cases
    for tc in ex['test_cases']:
        print(f"  Test: comparison_type={tc['comparison_type']}, expected_output={repr(tc['expected_output'])[:80]}")

print("\n=== Lesson 20: Form Handling in APIs ===")
for ex in ex20:
    print(f"\nExercise {ex['order']}: {ex['title']}")
    print(f"  Starter has import: {'import' in ex['starter_code'] or 'from' in ex['starter_code']}")
    print(f"  Solution has import: {'import' in ex['solution_code'] or 'from' in ex['solution_code']}")
    starter_lines = ex['starter_code'].strip().split('\n')
    print(f"  Starter first lines: {starter_lines[:3]}")
    for tc in ex['test_cases']:
        print(f"  Test: comparison_type={tc['comparison_type']}, expected_output={repr(tc['expected_output'])[:80]}")
