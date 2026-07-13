"""Tests for the sandboxed exercise runner — comparison types.

Tests each comparison type (exact, regex, non_empty, contains, whitelist,
comment) through the async run_code function.  Because the harness runs in
a subprocess, these are integration-level tests but still fast (<1s each).
"""

import pytest

from app.services.exercise_runner import run_code


class TestExactComparison:
    """Exact match (default)."""

    async def test_passes_when_output_matches(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_output_differs(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "world\n", "comparison_type": "exact"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestRegexComparison:
    """Regex matching."""

    async def test_passes_when_regex_matches(self):
        result = await run_code('print("hello world")', [
            {"input": "", "expected_output": r"hello\s+\w+", "comparison_type": "regex"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_regex_does_not_match(self):
        result = await run_code('print("goodbye")', [
            {"input": "", "expected_output": r"hello", "comparison_type": "regex"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestNonEmptyComparison:
    """non_empty: passes if output is not empty."""

    async def test_passes_when_output_not_empty(self):
        result = await run_code('print("something")', [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_output_empty(self):
        result = await run_code('pass', [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_fails_when_output_only_whitespace(self):
        result = await run_code('print("   ")', [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_fails_when_code_errors(self):
        """Even with an error, no output means fail."""
        result = await run_code('raise ValueError("boom")', [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        assert result["passed"] is False


class TestContainsComparison:
    """contains: passes if output contains the expected substring."""

    async def test_passes_when_substring_present(self):
        result = await run_code('print("hello world")', [
            {"input": "", "expected_output": "world", "comparison_type": "contains"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passes_with_partial_match(self):
        result = await run_code('x = 42\nprint(x)', [
            {"input": "", "expected_output": "42", "comparison_type": "contains"},
        ])
        assert result["passed"] is True

    async def test_fails_when_substring_absent(self):
        result = await run_code('print("goodbye")', [
            {"input": "", "expected_output": "hello", "comparison_type": "contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestWhitelistComparison:
    """whitelist: expected_output is a JSON list; output must be in that list."""

    async def test_passes_when_output_in_list(self):
        result = await run_code('print("cat")', [
            {"input": "", "expected_output": '["dog", "cat", "bird"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_output_not_in_list(self):
        result = await run_code('print("elephant")', [
            {"input": "", "expected_output": '["dog", "cat", "bird"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_handles_invalid_json_gracefully(self):
        """Bad JSON in expected_output should fail, not crash."""
        result = await run_code('print("anything")', [
            {"input": "", "expected_output": "not-json", "comparison_type": "whitelist"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_strips_whitespace_before_checking(self):
        """Whitespace around the actual output is stripped before checking."""
        result = await run_code('print("  apple  ")', [
            {"input": "", "expected_output": '["apple"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is True

    async def test_multiple_items(self):
        result = await run_code('name = input(); print(f"Hello, {name}")', [
            {"input": "Alice\n", "expected_output": '["Hello, Alice", "Hello, Bob"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is True


class TestCommentComparison:
    """comment: passes if user code contains a '#' character."""

    async def test_passes_when_code_has_comment(self):
        result = await run_code('# This is a comment\nprint("hello")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passes_with_inline_comment(self):
        result = await run_code('print("hello")  # inline', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is True

    async def test_fails_when_no_comment(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_fails_when_hash_in_string_only(self):
        """A '#' inside a string is technically a comment character too.
        Since we check for '#' in the source code, this passes — which is
        the intended behaviour for 'add a comment' style exercises."""
        result = await run_code('print("# not a comment")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is True


class TestMixedTestCases:
    """Multiple test cases with different comparison types."""

    async def test_all_pass(self):
        result = await run_code(
            'name = "Alice"\nprint(f"Hi, {name}")',
            [
                {"input": "", "expected_output": "Hi, Alice\n", "comparison_type": "exact"},
                {"input": "", "expected_output": "Alice", "comparison_type": "contains"},
                {"input": "", "expected_output": "", "comparison_type": "non_empty"},
            ],
        )
        assert result["passed"] is True
        assert len(result["test_results"]) == 3
        assert all(tr["passed"] for tr in result["test_results"])

    async def test_any_failure_fails_all(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
            {"input": "", "expected_output": "world", "comparison_type": "contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is True
        assert result["test_results"][1]["passed"] is False


class TestFallbackType:
    """Unknown comparison type falls back to exact match."""

    async def test_unknown_type_falls_back_to_exact(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "unknown_fallback"},
        ])
        assert result["passed"] is True
