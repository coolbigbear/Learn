#!/usr/bin/env python3
"""
Sandbox Harness — reads JSON from stdin, executes user code, outputs JSON to stdout.

Contract
--------
INPUT  (stdin, one JSON object):
  {
    "code": "print('hello')",
    "test_cases": [
      {
        "input": "Alice",
        "expected_output": "Hello, Alice!\\n",
        "comparison_type": "exact",       # exact | regex | non_empty | contains | whitelist | comment | code_contains | code_regex
        "name": "Test 1"                  # optional human-readable name
      }
    ]
  }

OUTPUT (stdout, one JSON object):
  {
    "passed": true,
    "actual_output": "Hello, Alice!\\n",
    "expected_output": "Hello, Alice!\\n",
    "errors": null,
    "test_results": [
      {
        "test_index": 0,
        "passed": true,
        "actual_output": "Hello, Alice!\\n",
        "expected_output": "Hello, Alice!\\n",
        "errors": null,
        "name": "Test 1",
        "message": null,
        "comparison_type": "exact"
      }
    ]
  }

All string fields are truncated to MAX_OUTPUT_CHARS (10 000 characters).
On any fatal error (parse failure, bad JSON, etc.) the harness prints a
minimal error JSON to stdout and exits 0 — the runner treats stdout as
the source of truth.
"""

import json
import sys
import textwrap

MAX_OUTPUT_CHARS = 10_000


def truncate(value: str | None, limit: int = MAX_OUTPUT_CHARS) -> str | None:
    """Truncate a string to *limit* characters, appending a notice if cut."""
    if value is None:
        return None
    if len(value) > limit:
        return value[:limit] + "... (truncated)"
    return value


def _check_exact(actual: str, expected: str) -> tuple[bool, str | None]:
    passed = actual == expected
    msg = None if passed else f"Expected: {expected!r}, but got: {actual!r}"
    return passed, msg


def _check_regex(actual: str, pattern: str) -> tuple[bool, str | None]:
    import re
    passed = bool(re.match(pattern, actual))
    msg = None if passed else f"Output does not match pattern: {pattern}"
    return passed, msg


def _check_non_empty(actual: str, expected: str) -> tuple[bool, str | None]:
    passed = bool(actual.strip())
    msg = None if passed else "Expected some output, but your code produced nothing"
    return passed, msg


def _check_contains(actual: str, expected: str) -> tuple[bool, str | None]:
    passed = expected in actual
    msg = None if passed else f"Expected output to contain: {expected!r}"
    return passed, msg


def _check_whitelist(actual: str, expected: str) -> tuple[bool, str | None]:
    try:
        allowed = json.loads(expected)
        passed = actual.strip() in allowed
        if not passed:
            msg = f'Output must be one of: {", ".join(repr(v) for v in allowed)}'
        else:
            msg = None
        return passed, msg
    except (json.JSONDecodeError, TypeError):
        return False, "Invalid test case (expected JSON list)"


def _check_comment(actual: str, expected: str, user_code: str) -> tuple[bool, str | None]:
    passed = "#" in user_code
    msg = None if passed else "Your code should include a comment (using #)"
    return passed, msg


def _check_comment_contains(actual: str, expected: str, user_code: str) -> tuple[bool, str | None]:
    import re
    comment_lines = []
    for _l in user_code.split("\n"):
        _s = _l.strip()
        if not _s:
            continue
        # Remove string contents to avoid false positives on # inside strings
        _no_strings = re.sub(r"'[^']*'", '""', re.sub(r'"[^"]*"', '""', _s))
        if "#" in _no_strings:
            idx = _no_strings.index("#")
            comment_lines.append(_s[idx:])
    if not comment_lines:
        return False, "Your code should include a comment (using #)"
    passed = any(expected in _cl for _cl in comment_lines)
    if not passed:
        return False, f"Your comment should contain: {expected!r}"
    return True, None


def _check_code_contains(actual: str, expected: str, user_code: str) -> tuple[bool, str | None]:
    passed = expected in user_code
    msg = None if passed else f"Your code should contain: {expected!r}"
    return passed, msg


def _check_code_regex(user_code: str, pattern: str) -> tuple[bool, str | None]:
    import re
    passed = bool(re.search(pattern, user_code))
    msg = None if passed else f"Your code does not match the required pattern"
    return passed, msg


def run_test_case(user_code: str, test_case: dict, index: int) -> dict:
    """Execute user code with the given test case and return result dict."""
    input_data = test_case.get("input", "")
    expected = test_case.get("expected_output", "")
    comparison = test_case.get("comparison_type", "exact")
    test_name = test_case.get("name")
    test_message = test_case.get("message")  # Human-readable message from test case

    # Redirect stdin/stdout/stderr
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    sys.stdin = _StdinCapture(input_data or "")
    sys.stdout = _StringIO()
    sys.stderr = _StringIO()

    # Restricted builtins for user code
    _builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    user_builtins = dict(_builtins)
    for _name in ("__import__", "exec", "eval", "compile", "open"):
        user_builtins.pop(_name, None)

    try:
        exec(user_code, {"__builtins__": user_builtins})
        actual_output = sys.stdout.getvalue()
        err_output = sys.stderr.getvalue()

        if comparison == "exact":
            passed, msg = _check_exact(actual_output, expected)
        elif comparison == "regex":
            passed, msg = _check_regex(actual_output, expected)
        elif comparison == "non_empty":
            passed, msg = _check_non_empty(actual_output, expected)
        elif comparison == "contains":
            passed, msg = _check_contains(actual_output, expected)
        elif comparison == "whitelist":
            passed, msg = _check_whitelist(actual_output, expected)
        elif comparison == "comment":
            passed, msg = _check_comment(actual_output, expected, user_code)
        elif comparison == "comment_contains":
            passed, msg = _check_comment_contains(actual_output, expected, user_code)
        elif comparison == "code_contains":
            passed, msg = _check_code_contains(actual_output, expected, user_code)
        elif comparison == "code_regex":
            passed, msg = _check_code_regex(user_code, expected)
        else:
            passed, msg = _check_exact(actual_output, expected)

        # Use test case message (human-readable) when provided and test fails
        if test_message is not None and not passed:
            msg = test_message

        return {
            "passed": passed,
            "actual_output": truncate(actual_output),
            "expected_output": truncate(expected),
            "errors": truncate(err_output) or None,
            "name": test_name,
            "message": msg,
            "comparison_type": comparison,
            "test_index": index,
        }
    except Exception as e:
        actual_output = sys.stdout.getvalue()
        return {
            "passed": False,
            "actual_output": truncate(actual_output),
            "expected_output": truncate(expected),
            "errors": f"{type(e).__name__}: {e}",
            "name": test_name,
            "message": f"Runtime error: {type(e).__name__}",
            "comparison_type": comparison,
            "test_index": index,
        }
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def run_code_only(user_code: str) -> dict:
    """When there are no test cases, just execute the code and capture output."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = _StringIO()
    sys.stderr = _StringIO()

    _builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    user_builtins = dict(_builtins)
    for _name in ("__import__", "exec", "eval", "compile", "open"):
        user_builtins.pop(_name, None)

    try:
        exec(user_code, {"__builtins__": user_builtins})
        actual = sys.stdout.getvalue()
        return {
            "passed": True,
            "actual_output": truncate(actual),
            "expected_output": "",
            "errors": None,
            "test_results": [],
        }
    except Exception as e:
        actual = sys.stdout.getvalue()
        return {
            "passed": False,
            "actual_output": truncate(actual),
            "expected_output": "",
            "errors": f"{type(e).__name__}: {e}",
            "test_results": [],
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def main():
    """Entry point: read JSON from stdin, run, print JSON to stdout."""
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({
            "passed": False,
            "actual_output": "",
            "expected_output": "",
            "errors": "No input received",
            "test_results": [],
        }))
        return

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "passed": False,
            "actual_output": "",
            "expected_output": "",
            "errors": f"Invalid JSON input: {e}",
            "test_results": [],
        }))
        return

    user_code = payload.get("code", "")
    test_cases = payload.get("test_cases", [])

    if not user_code.strip():
        print(json.dumps({
            "passed": False,
            "actual_output": "",
            "expected_output": "",
            "errors": "No code provided",
            "test_results": [],
        }))
        return

    if not test_cases:
        result = run_code_only(user_code)
        print(json.dumps(result))
        return

    results = []
    all_passed = True
    for i, tc in enumerate(test_cases):
        r = run_test_case(user_code, tc, i)
        if not r["passed"]:
            all_passed = False
        results.append(r)

    first = results[0]
    output = {
        "passed": all_passed,
        "actual_output": first["actual_output"],
        "expected_output": test_cases[0].get("expected_output", ""),
        "comparison_type": test_cases[0].get("comparison_type", "exact"),
        "errors": first.get("errors"),
        "test_results": results,
    }
    print(json.dumps(output))


# ── Replacements for sys.stdin / sys.stdout / sys.stderr ────────────────────

class _StringIO:
    """Minimal StringIO that the harness uses for stdout/stderr capture."""
    def __init__(self):
        self._buf = []

    def write(self, s: str):
        self._buf.append(s)

    def getvalue(self) -> str:
        return "".join(self._buf)

    def flush(self):
        pass

    def close(self):
        pass


class _StdinCapture:
    """Pretends to be stdin, returning *data* on read calls."""
    def __init__(self, data: str):
        self._data = data
        self._pos = 0

    def read(self, size: int = -1) -> str:
        if size < 0:
            rest = self._data[self._pos:]
            self._pos = len(self._data)
            return rest
        chunk = self._data[self._pos:self._pos + size]
        self._pos += size
        return chunk

    def readline(self, size: int = -1) -> str:
        idx = self._data.find("\n", self._pos)
        if idx == -1:
            return self.read(size)
        end = idx + 1
        if 0 <= size < (end - self._pos):
            return self.read(size)
        chunk = self._data[self._pos:end]
        self._pos = end
        return chunk

    def readlines(self, hint: int = -1) -> list[str]:
        lines = []
        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
        return lines

    def close(self):
        pass


if __name__ == "__main__":
    main()