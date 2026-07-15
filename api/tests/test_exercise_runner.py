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


class TestCommentContainsComparison:
    """comment_contains: passes if a comment line contains the expected substring."""

    async def test_passes_when_comment_contains_expected(self):
        result = await run_code('# This program prints numbers\nprint(10)', [
            {"input": "", "expected_output": "# This program prints numbers", "comparison_type": "comment_contains"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passes_with_inline_comment_containing_expected(self):
        result = await run_code('print("hello")  # Prints a greeting', [
            {"input": "", "expected_output": "# Prints a greeting", "comparison_type": "comment_contains"},
        ])
        assert result["passed"] is True

    async def test_fails_when_expected_text_not_in_comment(self):
        """Comment exists but doesn't contain the expected text."""
        result = await run_code('# This is wrong\nprint(10)', [
            {"input": "", "expected_output": "# This program prints numbers", "comparison_type": "comment_contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_fails_when_no_comment_at_all(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "# Some comment", "comparison_type": "comment_contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_fails_when_expected_text_in_string_but_not_comment(self):
        """Text appears in a string literal, not a comment — should fail."""
        result = await run_code('x = "# This program prints numbers"\nprint(x)', [
            {"input": "", "expected_output": "# This program prints numbers", "comparison_type": "comment_contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_failure_message_when_no_comment(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "# Some comment", "comparison_type": "comment_contains"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "comment" in msg.lower()

    async def test_failure_message_when_comment_wrong(self):
        result = await run_code('# Wrong comment\nprint("hello")', [
            {"input": "", "expected_output": "# Expected text", "comparison_type": "comment_contains"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "contain" in msg.lower()


class TestCodeContainsComparison:
    """code_contains: passes if user code contains the expected substring."""

    async def test_passes_when_code_contains_single_quote(self):
        """Exercise 3-style: check that submitted code uses a single quote."""
        result = await run_code("print('Greetings, Earthling!')", [
            {"input": "", "expected_output": "'", "comparison_type": "code_contains"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passes_when_code_contains_double_quote(self):
        """Specifically looks for double quotes in the code."""
        result = await run_code('print("Hello")', [
            {"input": "", "expected_output": '"', "comparison_type": "code_contains"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_code_does_not_contain_expected(self):
        result = await run_code('print("no singles here")', [
            {"input": "", "expected_output": "'", "comparison_type": "code_contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_passes_with_single_quote_and_double_quotes_both_present(self):
        """Mixed quotes — code contains the expected ' character."""
        result = await run_code("print('hello \"world\"')", [
            {"input": "", "expected_output": "'", "comparison_type": "code_contains"},
        ])
        assert result["passed"] is True

    async def test_failure_message(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "'", "comparison_type": "code_contains"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "contain" in msg.lower()

    async def test_no_message_on_success(self):
        result = await run_code("print('hello')", [
            {"input": "", "expected_output": "'", "comparison_type": "code_contains"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is None


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


class TestNamePropagation:
    """Test that the 'name' field is propagated from test cases to results."""

    async def test_name_propagated_when_provided(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact", "name": "Print greeting"},
        ])
        assert result["test_results"][0]["name"] == "Print greeting"

    async def test_name_is_none_when_not_provided(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        assert result["test_results"][0]["name"] is None

    async def test_name_propagated_on_error(self):
        result = await run_code('raise ValueError("boom")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact", "name": "Bad code"},
        ])
        assert result["test_results"][0]["name"] == "Bad code"


class TestFailureMessages:
    """Test that descriptive failure messages are generated for each comparison type."""

    async def test_exact_failure_message(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "world\n", "comparison_type": "exact"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "Expected:" in msg
        assert "hello" in msg
        assert "world" in msg

    async def test_regex_failure_message(self):
        result = await run_code('print("goodbye")', [
            {"input": "", "expected_output": r"hello", "comparison_type": "regex"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "pattern" in msg.lower()

    async def test_non_empty_failure_message(self):
        result = await run_code('pass', [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "nothing" in msg.lower()

    async def test_contains_failure_message(self):
        result = await run_code('print("goodbye")', [
            {"input": "", "expected_output": "hello", "comparison_type": "contains"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "contain" in msg.lower()

    async def test_whitelist_failure_message(self):
        result = await run_code('print("unknown")', [
            {"input": "", "expected_output": '["a", "b"]', "comparison_type": "whitelist"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "one of" in msg.lower()

    async def test_comment_failure_message(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "comment" in msg.lower()

    async def test_comment_contains_failure_message(self):
        result = await run_code('# Wrong\nprint("hello")', [
            {"input": "", "expected_output": "# Expected text", "comparison_type": "comment_contains"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "contain" in msg.lower()

    async def test_runtime_error_message(self):
        result = await run_code('raise ValueError("boom")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "Runtime error" in msg

    async def test_no_message_on_success(self):
        result = await run_code('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is None
