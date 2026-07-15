"""
Minimal test of comment_contains comparison type directly.
"""
import sys, json, subprocess, textwrap, tempfile
from pathlib import Path

USER_CODE = "# This program prints numbers\nprint(10)"
TEST_CASES = [
    {"input": "", "expected_output": "# This program prints numbers", "comparison_type": "comment_contains"},
]

# Use triple braces to escape format strings
HARNESS = """\
import io, json, sys

_USER_CODE = {user_code!r}

_TEST_CASES = {test_cases!r}

def _run_single(input_data, expected, comparison, test_name=None, message=None):
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdin = io.StringIO(input_data or '')
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        if comparison == 'comment_contains':
            comment_lines = [_l.strip() for _l in _USER_CODE.split('\\n') if _l.strip().startswith('#')]
            if not comment_lines:
                passed = False
                msg = 'Your code should include a comment (using #)'
            else:
                passed = any(expected in _cl for _cl in comment_lines)
                if not passed:
                    msg = f'Your comment should contain: {{expected!r}}'
                else:
                    msg = None
            actual = sys.stdout.getvalue()
        else:
            exec(_USER_CODE)
            actual = sys.stdout.getvalue()
            passed = False
            msg = None
        return {{'passed': passed, 'actual_output': actual, 'expected_output': expected, 'errors': None, 'name': test_name, 'message': msg, 'comparison_type': comparison}}
    except Exception as e:
        actual = sys.stdout.getvalue()
        return {{'passed': False, 'actual_output': actual, 'expected_output': expected, 'errors': f'{{type(e).__name__}}: {{e}}', 'name': test_name, 'message': f'Runtime error: {{type(e).__name__}}', 'comparison_type': comparison}}
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        sys.stderr = old_stderr

results = []
all_passed = True
for i, tc in enumerate(_TEST_CASES):
    r = _run_single(tc.get('input', ''), tc.get('expected_output', ''), tc.get('comparison_type', 'exact'), test_name=tc.get('name'), message=tc.get('message'))
    r['test_index'] = i
    if not r['passed']:
        all_passed = False
    results.append(r)

if results:
    first = results[0]
    print(json.dumps({{
        'passed': all_passed,
        'actual_output': first['actual_output'],
        'expected_output': _TEST_CASES[0].get('expected_output', '') if _TEST_CASES else '',
        'comparison_type': _TEST_CASES[0].get('comparison_type', 'exact') if _TEST_CASES else 'exact',
        'errors': first['errors'],
        'test_results': results
    }}))
"""

script = textwrap.dedent(HARNESS).format(user_code=USER_CODE, test_cases=TEST_CASES)

with tempfile.TemporaryDirectory(prefix="py_test_") as tmpdir:
    script_path = Path(tmpdir) / "runner.py"
    script_path.write_text(script)
    print("--- running ---")
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True, timeout=5, cwd=tmpdir,
    )
    print(f"stdout: {proc.stdout}")
    print(f"stderr: {proc.stderr}")
    print(f"returncode: {proc.returncode}")
    if proc.stdout:
        result = json.loads(proc.stdout)
        print(f"result: {json.dumps(result, indent=2)}")