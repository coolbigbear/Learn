"""Sandboxed Python exercise execution engine.

Runs user-submitted Python code in a subprocess with strict resource limits.
Uses `resource.setrlimit` for CPU time and memory caps, and SIGALRM for
wall-clock timeout.  Each execution happens in a fresh subprocess so the
parent (the API server) is never corrupted.

When DOCKER_ENABLED is True (in config.py), the `run_code_with_docker_fallback`
function tries the Docker sandbox first and falls back to the subprocess if
Docker is unavailable.
"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from app.config import (
    DOCKER_ENABLED,
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

def _run_single(input_data, expected, comparison, test_name=None, message=None):
    '''Run user code with given stdin and compare output.'''
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdin = io.StringIO(input_data or '')
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    # Build restricted builtins for user code (exec can't see open/exec/...)
    # Note: __import__ is NOT restricted — user code needs to import stdlib modules
    # (csv, io, json, re, math, etc.) for exercises. The subprocess + resource limits
    # provide adequate isolation.
    user_builtins = dict(_builtins)
    for _name in ('exec', 'eval', 'compile', 'open'):
        user_builtins.pop(_name, None)

    try:
        exec(_USER_CODE, {{'__builtins__': user_builtins}})
        actual = sys.stdout.getvalue()
        err = sys.stderr.getvalue()
        if comparison == 'exact':
            passed = (actual == expected)
            if not passed:
                msg = f'Expected: {{expected!r}}, but got: {{actual!r}}'
            else:
                msg = None
        elif comparison == 'regex':
            import re
            passed = bool(re.match(expected, actual))
            if not passed:
                msg = f'Output does not match pattern: {{expected}}'
            else:
                msg = None
        elif comparison == 'non_empty':
            passed = bool(actual.strip())
            if not passed:
                msg = 'Expected some output, but your code produced nothing'
            else:
                msg = None
        elif comparison == 'contains':
            passed = expected in actual
            if not passed:
                msg = f'Expected output to contain: {{expected!r}}'
            else:
                msg = None
        elif comparison == 'whitelist':
            import json as _json
            try:
                allowed = _json.loads(expected)
                passed = actual.strip() in allowed
                if not passed:
                    msg = f'Output must be one of: {{", ".join(repr(v) for v in allowed)}}'
                else:
                    msg = None
            except (_json.JSONDecodeError, TypeError):
                passed = False
                msg = 'Invalid test case (expected JSON list)'
        elif comparison == 'comment':
            passed = '#' in _USER_CODE
            if not passed:
                msg = 'Your code should include a comment (using #)'
            else:
                msg = None
        elif comparison == 'comment_contains':
            # Extract comment text from lines, handling both pure comment lines
            # and inline comments while ignoring # inside string literals
            import re as _re
            comment_lines = []
            for _l in _USER_CODE.split('\\\\n'):
                _s = _l.strip()
                if not _s:
                    continue
                # Remove string contents to avoid false positives on # inside strings
                _no_strings = _re.sub(r"'[^']*'", '""', _re.sub(r'"[^"]*"', '""', _s))
                if '#' in _no_strings:
                    idx = _no_strings.index('#')
                    comment_lines.append(_s[idx:])
            if not comment_lines:
                passed = False
                msg = 'Your code should include a comment (using #)'
            else:
                passed = any(expected in _cl for _cl in comment_lines)
                if not passed:
                    msg = f'Your comment should contain: {{expected!r}}'
                else:
                    msg = None
        elif comparison == 'code_contains':
            passed = expected in _USER_CODE
            if not passed:
                msg = f'Your code should contain: {{expected!r}}'
            else:
                msg = None
        elif comparison == 'code_regex':
            import re
            passed = bool(re.search(expected, _USER_CODE))
            if not passed:
                msg = f'Your code does not match the required pattern'
            else:
                msg = None
        else:
            passed = (actual == expected)
            if not passed:
                msg = f'Expected: {{expected!r}}, but got: {{actual!r}}'
            else:
                msg = None
        # Use human-readable message from test case when provided and test fails
        if message is not None and not passed:
            msg = message
        return {{'passed': passed, 'actual_output': actual, 'expected_output': expected, 'errors': err or None, 'name': test_name, 'message': msg, 'comparison_type': comparison}}
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

# Aggregate
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
else:
    # No test cases -- just run the code
    user_builtins = dict(_builtins)
    # __import__ is NOT restricted — user code needs stdlib imports
    for _name in ('exec', 'eval', 'compile', 'open'):
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
        }}), file=old_stdout)
    except Exception as e:
        actual = sys.stdout.getvalue()
        print(json.dumps({{
            'passed': False,
            'actual_output': actual,
            'expected_output': '',
            'errors': f'{{type(e).__name__}}: {{e}}',
            'test_results': []
        }}), file=old_stdout)
    finally:
        sys.stdout = old_stdout
"""

TEST_SUITE_HARNESS_TEMPLATE = """\
# Harness: wraps user code + test_suite, discovers and runs test_* functions,
# outputs JSON results.
# This script runs inside the sandbox subprocess.  The sandbox runner
# grants it full builtins (import, exec, open, etc.) so that the harness
# itself can function.

import importlib.util
import json
import sys
import traceback


# 1. Write user code to exercise.py
_USER_CODE = {user_code!r}
with open('exercise.py', 'w') as _f:
    _f.write(_USER_CODE)

# 2. Write test suite to test_suite.py
_TEST_SUITE = {test_suite!r}
with open('test_suite.py', 'w') as _f:
    _f.write(_TEST_SUITE)

# 3. Import user code as the 'exercise' module via importlib
_spec = importlib.util.spec_from_file_location('exercise', 'exercise.py')
_exercise = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_exercise)

# 4. Execute test suite in a namespace that has 'exercise'
_test_ns = {{'exercise': _exercise}}
exec(open('test_suite.py').read(), _test_ns)

# 5. Discover test_* functions
_test_funcs = [(name, fn) for name, fn in _test_ns.items() if name.startswith('test_')]
_test_funcs.sort(key=lambda x: x[0])

# 6. Run each test, collect results
_results = []
_all_passed = True
for _i, (_name, _fn) in enumerate(_test_funcs):
    try:
        _fn()
        _results.append({{
            'test_index': _i,
            'name': _name,
            'passed': True,
            'message': None,
            'actual_output': '',
            'expected_output': '',
            'errors': None,
            'comparison_type': 'exact'
        }})
    except AssertionError as _e:
        _all_passed = False
        _results.append({{
            'test_index': _i,
            'name': _name,
            'passed': False,
            'message': str(_e) if str(_e) else 'Assertion failed',
            'actual_output': '',
            'expected_output': '',
            'errors': None,
            'comparison_type': 'exact'
        }})
    except Exception as _e:
        _all_passed = False
        _results.append({{
            'test_index': _i,
            'name': _name,
            'passed': False,
            'message': f'{{type(_e).__name__}}: {{_e}}',
            'actual_output': '',
            'expected_output': '',
            'errors': f'{{type(_e).__name__}}: {{_e}}',
            'comparison_type': 'exact'
        }})

print(json.dumps({{
    'passed': _all_passed,
    'actual_output': '',
    'expected_output': '',
    'errors': None,
    'test_results': _results
}}))
"""


def _build_runner_script(user_code: str, test_cases: list[dict]) -> str:
    """Build a self-contained Python script that wraps user code + test cases."""
    script = HARNESS_TEMPLATE.format(
        user_code=user_code,
        test_cases=test_cases,
    )
    return textwrap.dedent(script)


def _build_test_suite_runner(user_code: str, test_suite: str) -> str:
    """Build a harness script that writes user code + test_suite to disk and runs tests.

    The generated script:
    1. Writes user code to exercise.py
    2. Writes test suite code to test_suite.py
    3. Imports user code via importlib (proper module semantics)
    4. Executes test suite to define test_* functions
    5. Runs each test function, catching AssertionError and other exceptions
    6. Outputs JSON in the standard RunResult format
    """
    script = TEST_SUITE_HARNESS_TEMPLATE.format(
        user_code=user_code,
        test_suite=test_suite,
    )
    return textwrap.dedent(script)


async def run_code(
    user_code: str,
    test_cases: list[dict],
    test_suite: str | None = None,
) -> dict:
    """Execute user code against test cases or test_suite in a sandboxed subprocess.

    When *test_suite* is provided, the harness writes user code to ``exercise.py``
    and the test suite to ``test_suite.py``, then discovers and runs ``test_*``
    functions via importlib.  Test functions access user code through the
    ``exercise`` module (e.g. ``exercise.add(1, 2)``).

    When *test_suite* is *None* (default), falls back to the existing
    test_cases-based execution.

    Returns a dict with keys: passed, actual_output, expected_output, errors, test_results.
    """
    if test_suite is not None:
        script = _build_test_suite_runner(user_code, test_suite)
    else:
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


async def run_code_with_docker_fallback(
    user_code: str,
    test_cases: list[dict],
    language: str = "python",
    test_suite: str | None = None,
) -> dict:
    """Run user code using Docker with fallback to subprocess.

    Tries the Docker sandbox first (when DOCKER_ENABLED is True). If Docker
    is unavailable, falls back gracefully to the subprocess runner.
    When *test_suite* is provided, the Docker runner is skipped and the
    subprocess test_suite runner is used directly.

    Returns the same dict schema as run_code().
    """
    # When test_suite is present, skip Docker and use subprocess test_suite runner
    if test_suite is not None:
        return await run_code(user_code, test_cases, test_suite=test_suite)

    if DOCKER_ENABLED:
        try:
            from app.services.docker_runner import run_code_in_docker

            return await run_code_in_docker(user_code, test_cases, language)
        except ImportError:
            # docker package not installed — fall through
            pass
        except Exception:
            # Docker unavailable or error — fall through to subprocess
            pass

    # Fallback: use the subprocess runner (language parameter is not used
    # by the subprocess runner since it only supports Python)
    return await run_code(user_code, test_cases, test_suite=test_suite)
