#!/usr/bin/env python3
"""Test all ML exercise solutions locally."""
import json, sys, io, traceback

lessons = [
    '21-intro-to-ml',
    '22-data-preprocessing',
    '23-supervised-learning',
    '24-unsupervised-learning',
]

passed = 0
failed = 0

for slug in lessons:
    path = f'/home/pi2/.hermes/projects/python-tutorials/content/{slug}/exercises.json'
    with open(path) as f:
        exercises = json.load(f)
    
    for ex in exercises:
        ex_slug = ex['slug']
        solution = ex.get('solution_code', '')
        test_cases = ex.get('test_cases', [])
        
        print(f"\n{slug} / {ex_slug}...", end=" ")
        
        if not solution:
            print("SKIP (no solution)")
            continue
        
        for tc in test_cases:
            expected = tc.get('expected_output', '')
            comparison = tc.get('comparison_type', 'exact')
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                exec(solution, {'__builtins__': __builtins__})
                actual = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                if comparison == 'exact':
                    ok = (actual == expected)
                elif comparison == 'contains':
                    ok = (expected in actual)
                elif comparison == 'regex':
                    import re
                    ok = bool(re.match(expected, actual))
                else:
                    ok = False
                
                if ok:
                    passed += 1
                    print("PASS", end=" ")
                else:
                    failed += 1
                    print("FAIL", end=" ")
                    if actual != expected:
                        print(f"\n  Expected: {expected[:100]!r}")
                        print(f"  Got:      {actual[:100]!r}")
            except Exception as e:
                sys.stdout = old_stdout
                failed += 1
                print(f"ERROR: {type(e).__name__}: {e}", end=" ")

        if not test_cases:
            print("(no tests)", end=" ")

print(f"\n\n{'='*50}")
print(f"Total: {passed} passed, {failed} failed out of {passed+failed}")
