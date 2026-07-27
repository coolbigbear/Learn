"""Tests for the test_suite execution mode in exercise_runner.

The test_suite mode accepts a raw Python string containing test_* functions
that use `exercise.` prefix to reference user code, with plain `assert`
statements for verification.
"""

import pytest

from app.services.exercise_runner import _build_test_suite_runner, run_code


# ---------------------------------------------------------------------------
# _build_test_suite_runner --- static script generation
# ---------------------------------------------------------------------------

class TestBuildTestSuiteRunner:
    """Unit-level checks on the generated harness script."""

    def test_returns_string(self):
        """The function should return a non-empty string."""
        script = _build_test_suite_runner("print('hello')", "def test_a(): pass")
        assert isinstance(script, str)
        assert len(script) > 100

    def test_includes_key_elements(self):
        """The generated script should contain importlib, exercise.py, and test_suite.py mentions."""
        script = _build_test_suite_runner("print('hello')", "def test_a(): pass")
        # Must write user code and test suite to disk
        assert "exercise.py" in script
        assert "test_suite.py" in script
        # Must use importlib for proper module import
        assert "importlib.util" in script or "importlib" in script
        # Must discover test_* functions
        assert "test_" in script
        # Must output JSON
        assert "json.dumps" in script or "json.dump" in script


class TestBuildTestSuiteRunnerValidSyntax:
    """Verify the generated script is syntactically valid Python."""

    def test_syntax_passing_user_code(self):
        """The generated harness should be syntactically valid Python."""
        script = _build_test_suite_runner(
            "def add(a, b):\n    return a + b",
            "def test_passes():\n    result = exercise.add(1, 2)\n    assert result == 3",
        )
        compile(script, "<test-harness>", "exec")

    def test_syntax_with_multiline_user_code(self):
        """Multiline user code should produce valid harness."""
        script = _build_test_suite_runner(
            "def greet(name):\n    return f'Hello, {name}!'",
            "def test_greet():\n    result = exercise.greet('Alice')\n    assert result == 'Hello, Alice!'",
        )
        compile(script, "<test-harness>", "exec")


# ---------------------------------------------------------------------------
# run_code integration --- test_suite mode end-to-end
# ---------------------------------------------------------------------------

class TestRunCodeWithTestSuite:
    """End-to-end tests of run_code() with test_suite parameter."""

    async def test_passes_when_all_assertions_pass(self):
        """When all test_* functions pass, passed should be True."""
        result = await run_code(
            user_code="def add(a, b):\n    return a + b",
            test_cases=[],  # ignored when test_suite is present
            test_suite=(
                "def test_adds_correctly():\n"
                "    result = exercise.add(2, 3)\n"
                "    assert result == 5\n"
                "def test_adds_zero():\n"
                "    result = exercise.add(0, 0)\n"
                "    assert result == 0\n"
            ),
        )
        assert result["passed"] is True
        assert len(result["test_results"]) == 2
        assert all(tr["passed"] for tr in result["test_results"])

    async def test_fails_when_assertion_fails(self):
        """When a test_* function raises AssertionError, passed should be False."""
        result = await run_code(
            user_code="def add(a, b):\n    return a + b",
            test_cases=[],
            test_suite=(
                "def test_adds_correctly():\n"
                "    result = exercise.add(2, 3)\n"
                "    assert result == 5\n"
                "def test_adds_wrong():\n"
                "    result = exercise.add(2, 3)\n"
                "    assert result == 99, 'Expected 99, got ' + str(result)\n"
            ),
        )
        assert result["passed"] is False
        assert len(result["test_results"]) == 2
        # First test passed, second failed
        assert result["test_results"][0]["passed"] is True
        assert result["test_results"][1]["passed"] is False
        assert result["test_results"][1]["message"] is not None
        assert "99" in result["test_results"][1]["message"] or "Expected" in result["test_results"][1]["message"]

    async def test_runtime_error_in_test_function(self):
        """An unexpected exception in a test function should be caught."""
        result = await run_code(
            user_code="def add(a, b):\n    return a + b",
            test_cases=[],
            test_suite=(
                "def test_crashes():\n"
                "    raise ValueError('something went wrong')\n"
            ),
        )
        assert result["passed"] is False
        assert len(result["test_results"]) == 1
        assert result["test_results"][0]["passed"] is False
        assert result["test_results"][0]["errors"] is not None

    async def test_tests_refer_to_exercise_module(self):
        """Test suite accesses user code via exercise module, not globals."""
        result = await run_code(
            user_code="def double(x):\n    return x * 2",
            test_cases=[],
            test_suite=(
                "def test_doubles_two():\n"
                "    assert exercise.double(2) == 4\n"
                "def test_doubles_three():\n"
                "    assert exercise.double(3) == 6\n"
            ),
        )
        assert result["passed"] is True
        assert len(result["test_results"]) == 2
        assert all(tr["passed"] for tr in result["test_results"])

    async def test_test_results_have_correct_structure(self):
        """Each test_result should have the expected keys."""
        result = await run_code(
            user_code="def double(x):\n    return x * 2",
            test_cases=[],
            test_suite="def test_doubles():\n    assert exercise.double(2) == 4\n",
        )
        assert result["passed"] is True
        tr = result["test_results"][0]
        assert "test_index" in tr
        assert "name" in tr
        assert "passed" in tr
        assert "message" in tr
        assert "actual_output" in tr
        assert "expected_output" in tr
        assert "errors" in tr
        assert "comparison_type" in tr
        assert tr["name"] == "test_doubles"
        assert tr["test_index"] == 0
        assert tr["comparison_type"] == "exact"


class TestRunCodeTestSuiteFallback:
    """Existing test_cases mode should still work when test_suite is None."""

    async def test_falls_back_to_test_cases_when_test_suite_none(self):
        """When test_suite is None, use test_cases as before."""
        result = await run_code(
            user_code='print("hello")',
            test_cases=[{"input": "", "expected_output": "hello\n", "comparison_type": "exact"}],
            test_suite=None,
        )
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_test_suite_takes_priority(self):
        """When both test_suite and test_cases are present, test_suite wins."""
        result = await run_code(
            user_code="def add(a, b):\n    return a + b",
            test_cases=[{"input": "", "expected_output": "WRONG\n", "comparison_type": "exact"}],
            test_suite=(
                "def test_adds():\n"
                "    assert exercise.add(2, 3) == 5\n"
            ),
        )
        # test_suite should take priority, ignoring the failing test_cases
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passing_no_test_cases_and_no_test_suite(self):
        """When both are empty/None, it should just run the code."""
        result = await run_code(
            user_code='print("hello")',
            test_cases=[],
            test_suite=None,
        )
        assert result["passed"] is True
        assert result["actual_output"] == "hello\n"


class TestRunCodeWithDockerFallback:
    """Test run_code_with_docker_fallback handles test_suite correctly."""

    async def test_runs_test_suite_when_provided(self):
        """run_code_with_docker_fallback should run test_suite when provided."""
        from app.services.exercise_runner import run_code_with_docker_fallback

        result = await run_code_with_docker_fallback(
            user_code="def double(x):\n    return x * 2",
            test_cases=[],
            test_suite=(
                "def test_doubles():\n"
                "    assert exercise.double(2) == 4\n"
            ),
        )
        assert result["passed"] is True
        assert len(result["test_results"]) == 1
        assert result["test_results"][0]["passed"] is True

    async def test_fallback_still_works_with_test_cases(self, monkeypatch):
        """Without test_suite, fallback should still work via test_cases."""
        monkeypatch.setattr("app.services.exercise_runner.DOCKER_ENABLED", False)
        from app.services.exercise_runner import run_code_with_docker_fallback

        result = await run_code_with_docker_fallback(
            user_code='print("hello")',
            test_cases=[{"input": "", "expected_output": "hello\n", "comparison_type": "exact"}],
        )
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True
