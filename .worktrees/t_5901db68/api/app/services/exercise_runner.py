"""Sandboxed Python exercise execution engine.

Runs user-submitted Python code in a subprocess with strict resource limits.
Uses `resource.setrlimit` for CPU time and memory caps, and SIGALRM for
wall-clock timeout.  Each execution happens in a fresh subprocess so the
parent (the API server) is never corrupted.
"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from app.config import (
    MAX_CPU_SECONDS,
    MAX_MEMORY_MB,
    MAX_OUTPUT_CHARS,
    SHELL_TIMEOUT,
)

HARNESS_TEMPLATE = """\
# Harness: wraps user code, runs test cases, outputs JSON results.
# This script runs inside the sandbox subprocess.  The sandbox runner
# grants it full builtins (import, exec, open, etc.) so that the harness
# itself can function.  Only user code gets restricted builtins.

import io
import json
import sys

# Capture original builtins for user-code exec (the sandbox runner
# gives us the real builtins -- we restrict them ourselves).
_builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__

# User code
_USER_CODE = {user_code!r}

# Test cases
_TEST_CASES = {test_cases!r}

def _run_single(input_data, expected, comparison):
    '''Run user code with given stdin and compare output.'''
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdin = io.StringIO(input_data or '')
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    # Build restricted builtins for user code (exec can't see open/exec/...)
    user_builtins = dict(_builtins)
    for _name in ('__import__', 'exec', 'eval', 'compile', 'open'):
        user_builtins.pop(_name, None)

    try:
        exec(_USER_CODE, {{'__builtins__': user_builtins}})
        actual = sys.stdout.getvalue()
        err = sys.stderr.getvalue()
        if comparison == 'exact':
            passed = (actual == expected)
        elif comparison == 'regex':
            import re
            passed = bool(re.match(expected, actual))
        elif comparison == 'non_empty':
            passed = bool(actual.strip())
        elif comparison == 'contains':
            passed = expected in actual
        elif comparison == 'whitelist':
            import json as _json
            try:
                allowed = _json.loads(expected)
                passed = actual.strip() in allowed
            except (_json.JSONDecodeError, TypeError):
                passed = False
        elif comparison == 'comment':
            passed = '#' in _USER_CODE
        else:
            passed = (actual == expected)
        return {{'passed': passed, 'actual_output': actual, 'expected_output': expected, 'errors': err or None}}
    except Exception as e:
        actual = sys.stdout.getvalue()
        return {{'passed': False, 'actual_output': actual, 'expected_output': expected, 'errors': f'{{type(e).__name__}}: {{e}}'}}
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        sys.stderr = old_stderr

results = []
all_passed = True
for i, tc in enumerate(_TEST_CASES):
    r = _run_single(tc.get('input', ''), tc.get('expected_output', ''), tc.get('comparison_type', 'exact'))
    r['test_index'] = i
    if not r['passed']:
        all_passed = False
    results.append(r)

# Aggregate
if results:
    first = results[0]
    print(json.dumps({{
        'passed': all_passed,
        'actual_output': first['actual_output'],
        'expected_output': _TEST_CASES[0].get('expected_output', '') if _TEST_CASES else '',
        'errors': first['errors'],
        'test_results': results
    }}))
else:
    # No test cases -- just run the code
    user_builtins = dict(_builtins)
    for _name in ('__import__', 'exec', 'eval', 'compile', 'open'):
        user_builtins.pop(_name, None)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exec(_USER_CODE, {{'__builtins__': user_builtins}})
        actual = sys.stdout.getvalue()
        print(json.dumps({{
            'passed': True,
            'actual_output': actual,
            'expected_output': '',
            'errors': None,
            'test_results': []
        }}))
    except Exception as e:
        actual = sys.stdout.getvalue()
        print(json.dumps({{
            'passed': False,
            'actual_output': actual,
            'expected_output': '',
            'errors': f'{{type(e).__name__}}: {{e}}',
            'test_results': []
        }}))
    finally:
        sys.stdout = old_stdout
"""


def _build_runner_script(user_code: str, test_cases: list[dict]) -> str:
    """Build a self-contained Python script that wraps user code + test cases."""
    script = HARNESS_TEMPLATE.format(
        user_code=user_code,
        test_cases=test_cases,
    )
    return textwrap.dedent(script)


async def run_code(user_code: str, test_cases: list[dict]) -> dict:
    """Execute user code against test cases in a sandboxed subprocess.

    Returns a dict with keys: passed, actual_output, expected_output, errors, test_results.
    """
    script = _build_runner_script(user_code, test_cases)

    with tempfile.TemporaryDirectory(prefix="py_sandbox_") as tmpdir:
        script_path = Path(tmpdir) / "runner.py"
        script_path.write_text(script)

        # Build the resource-limited sandbox runner.
        # This script sets resource limits, then execs the harness.
        # Builtins are NOT disabled at this level so the harness can import stdlib.
        runner_code = textwrap.dedent(f"""\
            import json, os, resource, signal, sys

            # Resource limits
            resource.setrlimit(resource.RLIMIT_CPU, ({MAX_CPU_SECONDS}, {MAX_CPU_SECONDS}))
            mem_bytes = {MAX_MEMORY_MB} * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

            # Wall-clock timeout
            def timeout_handler(signum, frame):
                print(json.dumps({{'passed': False, 'actual_output': '', 'expected_output': '', 'errors': 'Timeout: execution took too long', 'test_results': []}}))
                sys.exit(1)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm({MAX_CPU_SECONDS + 1})

            # Execute the harness
            exec(open({str(script_path)!r}).read())
        """)

        runner_path = Path(tmpdir) / "sandbox_runner.py"
        runner_path.write_text(runner_code)

        try:
            proc = subprocess.run(
                [sys.executable, str(runner_path)],
                capture_output=True,
                text=True,
                timeout=SHELL_TIMEOUT,
                cwd=tmpdir,
                env={"PYTHONPATH": tmpdir, "PATH": os.environ.get("PATH", "")},
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "actual_output": "",
                "expected_output": "",
                "errors": "Execution timed out",
                "test_results": [],
            }

        # Parse stdout as JSON
        output_text = proc.stdout.strip() or ""
        stderr_text = proc.stderr.strip() or ""

        if output_text:
            try:
                result = json.loads(output_text)
                # Truncate long outputs
                for key in ("actual_output", "expected_output", "errors"):
                    if isinstance(result.get(key), str) and len(result[key]) > MAX_OUTPUT_CHARS:
                        result[key] = result[key][:MAX_OUTPUT_CHARS] + "... (truncated)"
                for tr in result.get("test_results", []):
                    for key in ("actual_output", "expected_output", "errors"):
                        if isinstance(tr.get(key), str) and len(tr[key]) > MAX_OUTPUT_CHARS:
                            tr[key] = tr[key][:MAX_OUTPUT_CHARS] + "... (truncated)"
                return result
            except json.JSONDecodeError:
                return {
                    "passed": False,
                    "actual_output": output_text,
                    "expected_output": "",
                    "errors": stderr_text or "Failed to parse runner output",
                    "test_results": [],
                }

        # Fallback: no stdout, use stderr
        return {
            "passed": False,
            "actual_output": output_text,
            "expected_output": "",
            "errors": stderr_text or "No output produced",
            "test_results": [],
        }