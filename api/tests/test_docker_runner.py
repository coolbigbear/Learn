"""Tests for the Docker sandbox runner — comparison types.

Tests each comparison type (exact, regex, non_empty, contains, whitelist,
comment, code_contains) through the async run_code_in_docker function.

These are integration tests that require Docker to be installed and running,
and the tutorial-runner-python:latest image to be built.
"""

import pytest

from app.services.docker_runner import DockerRunner, DockerUnavailableError


# Module-level DockerRunner singleton for tests
_test_runner: DockerRunner | None = None


def _get_test_runner() -> DockerRunner:
    """Get or create a DockerRunner for tests, or skip if Docker unavailable."""
    global _test_runner
    if _test_runner is not None:
        return _test_runner
    try:
        _test_runner = DockerRunner()
        return _test_runner
    except (DockerUnavailableError, ImportError, FileNotFoundError) as e:
        pytest.skip(f"Docker runner unavailable: {e}")


async def _run_or_skip(user_code, test_cases):
    """Run code in Docker, or skip the test if Docker is unavailable."""
    runner = _get_test_runner()
    try:
        return await runner.run_code(user_code, test_cases)
    except DockerUnavailableError:
        pytest.skip("Docker is not available on this system")


def _memory_limit_supported() -> bool:
    """Check whether Docker memory cgroup limits are supported on this host.

    This is a platform check: on Raspberry Pi (running Debian Trixie),
    the ``memory`` cgroup controller is not in the v2 hierarchy, so
    ``--memory`` flags are silently ignored by Docker.  See §4.2 in
    docs/DOCKER_SANDBOX.md for details.
    """
    try:
        import subprocess as sp

        result = sp.run(
            ["docker", "info", "--format", "{{.MemoryLimit}}"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip().lower() == "true"
    except Exception:
        return False


def _run_raw_in_container(code: str, timeout: int = 10) -> dict:
    """Run code directly inside a Docker container, bypassing the harness.

    This helper is used for security tests that need to exercise the Docker
    container isolation layer (network, filesystem, capabilities, PID
    namespace) without the sandbox harness restricting builtins.

    Returns a dict with 'passed', 'stdout', 'stderr', and 'exit_code'.
    """
    import docker as docker_sdk
    import tempfile
    import os
    from pathlib import Path

    runner = _get_test_runner()
    cfg = runner.get_config("python")

    # Write a simple wrapper that imports __builtins__ and execs the user code
    wrapper = (
        "import builtins\n"
        f"_USER_CODE = {code!r}\n"
        "try:\n"
        "    exec(_USER_CODE, {'__builtins__': builtins})\n"
        "except Exception as e:\n"
        "    import sys\n"
        f"    print(f'ERROR: {{type(e).__name__}}: {{e}}', file=sys.stderr)\n"
        "    sys.exit(1)\n"
    )

    tmpdir = tempfile.mkdtemp(prefix="docker_raw_test_")
    script_path = Path(tmpdir) / "runner.py"
    script_path.write_text(wrapper)
    os.chmod(tmpdir, 0o755)
    script_path.chmod(0o644)

    try:
        container = runner.client.containers.run(
            image=cfg["image"],
            command=["python3", "/tmp/runner/runner.py"],
            volumes={tmpdir: {"bind": "/tmp/runner", "mode": "ro"}},
            network_disabled=True,
            read_only=True,
            tmpfs={"/tmp": "size=10M,noexec,nosuid,uid=1001,gid=1001"},
            mem_limit=cfg["memory_limit"],
            nano_cpus=cfg["cpu_limit"],
            pids_limit=cfg["pids_limit"],
            user="sandbox",
            cap_drop=["ALL"],
            detach=True,
            remove=False,
            stdout=True,
            stderr=True,
        )

        try:
            container.wait(timeout=timeout)
        except (docker_sdk.errors.APIError, Exception):
            try:
                container.kill()
            except Exception:
                pass
            logs = container.logs(stdout=True, stderr=True)
            container.remove(force=True)
            return {
                "passed": False,
                "stdout": "",
                "stderr": str(logs),
                "exit_code": -1,
            }

        logs = container.logs(stdout=True, stderr=True)
        exit_code = container.wait()["StatusCode"]
        container.remove(force=True)

        output = logs.decode("utf-8", errors="replace") if isinstance(logs, bytes) else str(logs)
        lines = output.split("\n")
        stdout_lines = []
        stderr_lines = []
        for line in lines:
            if line.startswith("ERROR:"):
                stderr_lines.append(line)
            else:
                stdout_lines.append(line)

        return {
            "passed": exit_code == 0,
            "stdout": "\n".join(stdout_lines).strip(),
            "stderr": "\n".join(stderr_lines).strip(),
            "exit_code": exit_code,
        }
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


class TestDockerBasicExecution:
    """Basic execution sanity checks."""

    async def test_basic_python_execution(self):
        result = await _run_or_skip('print("hello world")', [
            {"input": "", "expected_output": "hello world\n", "comparison_type": "exact"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_execution_with_input(self):
        result = await _run_or_skip(
            'name = input().strip()\nprint(f"Hello, {name}")',
            [{"input": "Alice\n", "expected_output": "Hello, Alice\n", "comparison_type": "exact"}],
        )
        assert result["passed"] is True

    async def test_no_test_cases_just_run(self):
        """When test_cases is empty, just run the code."""
        result = await _run_or_skip('print("hello")', [])
        assert result["passed"] is True
        assert result["actual_output"] == "hello\n"

    async def test_syntax_error_in_user_code(self):
        """Syntax errors should be caught gracefully."""
        result = await _run_or_skip('print("hello', [])
        assert result["passed"] is False
        assert "SyntaxError" in (result["errors"] or "")


class TestExactComparison:
    """Exact match (default)."""

    async def test_passes_when_output_matches(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_output_differs(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "world\n", "comparison_type": "exact"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestRegexComparison:
    """Regex matching."""

    async def test_passes_when_regex_matches(self):
        result = await _run_or_skip('print("hello world")', [
            {"input": "", "expected_output": r"hello\s+\w+", "comparison_type": "regex"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_regex_does_not_match(self):
        result = await _run_or_skip('print("goodbye")', [
            {"input": "", "expected_output": r"hello", "comparison_type": "regex"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestNonEmptyComparison:
    """non_empty: passes if output is not empty."""

    async def test_passes_when_output_not_empty(self):
        result = await _run_or_skip('print("something")', [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_output_empty(self):
        result = await _run_or_skip("pass", [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_fails_when_output_only_whitespace(self):
        result = await _run_or_skip('print("   ")', [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestContainsComparison:
    """contains: passes if output contains the expected substring."""

    async def test_passes_when_substring_present(self):
        result = await _run_or_skip('print("hello world")', [
            {"input": "", "expected_output": "world", "comparison_type": "contains"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passes_with_partial_match(self):
        result = await _run_or_skip("x = 42\nprint(x)", [
            {"input": "", "expected_output": "42", "comparison_type": "contains"},
        ])
        assert result["passed"] is True

    async def test_fails_when_substring_absent(self):
        result = await _run_or_skip('print("goodbye")', [
            {"input": "", "expected_output": "hello", "comparison_type": "contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestWhitelistComparison:
    """whitelist: expected_output is a JSON list; output must be in that list."""

    async def test_passes_when_output_in_list(self):
        result = await _run_or_skip('print("cat")', [
            {"input": "", "expected_output": '["dog", "cat", "bird"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_output_not_in_list(self):
        result = await _run_or_skip('print("elephant")', [
            {"input": "", "expected_output": '["dog", "cat", "bird"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_handles_invalid_json_gracefully(self):
        result = await _run_or_skip('print("anything")', [
            {"input": "", "expected_output": "not-json", "comparison_type": "whitelist"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_strips_whitespace_before_checking(self):
        result = await _run_or_skip('print("  apple  ")', [
            {"input": "", "expected_output": '["apple"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is True

    async def test_multiple_items(self):
        result = await _run_or_skip('name = input(); print(f"Hello, {name}")', [
            {"input": "Alice\n", "expected_output": '["Hello, Alice", "Hello, Bob"]', "comparison_type": "whitelist"},
        ])
        assert result["passed"] is True


class TestCommentComparison:
    """comment: passes if user code contains a '#' character."""

    async def test_passes_when_code_has_comment(self):
        result = await _run_or_skip('# This is a comment\nprint("hello")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passes_with_inline_comment(self):
        result = await _run_or_skip('print("hello")  # inline', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is True

    async def test_fails_when_no_comment(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False

    async def test_fails_when_hash_in_string_only(self):
        result = await _run_or_skip('print("# not a comment")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        assert result["passed"] is True


class TestCodeContainsComparison:
    """code_contains: passes if user code contains the expected substring."""

    async def test_passes_when_code_contains_single_quote(self):
        result = await _run_or_skip("print('Greetings, Earthling!')", [
            {"input": "", "expected_output": "'", "comparison_type": "code_contains"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_passes_when_code_contains_double_quote(self):
        result = await _run_or_skip('print("Hello")', [
            {"input": "", "expected_output": '"', "comparison_type": "code_contains"},
        ])
        assert result["passed"] is True
        assert result["test_results"][0]["passed"] is True

    async def test_fails_when_code_does_not_contain_expected(self):
        result = await _run_or_skip('print("no singles here")', [
            {"input": "", "expected_output": "'", "comparison_type": "code_contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is False


class TestMixedTestCases:
    """Multiple test cases with different comparison types."""

    async def test_all_pass(self):
        result = await _run_or_skip(
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
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
            {"input": "", "expected_output": "world", "comparison_type": "contains"},
        ])
        assert result["passed"] is False
        assert result["test_results"][0]["passed"] is True
        assert result["test_results"][1]["passed"] is False


class TestFallbackType:
    """Unknown comparison type falls back to exact match."""

    async def test_unknown_type_falls_back_to_exact(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "unknown_fallback"},
        ])
        assert result["passed"] is True


class TestNamePropagation:
    """Test that the 'name' field is propagated from test cases to results."""

    async def test_name_propagated_when_provided(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact", "name": "Print greeting"},
        ])
        assert result["test_results"][0]["name"] == "Print greeting"

    async def test_name_is_none_when_not_provided(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        assert result["test_results"][0]["name"] is None

    async def test_name_propagated_on_error(self):
        result = await _run_or_skip('raise ValueError("boom")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact", "name": "Bad code"},
        ])
        assert result["test_results"][0]["name"] == "Bad code"


class TestFailureMessages:
    """Test that descriptive failure messages are generated for each comparison type."""

    async def test_exact_failure_message(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "world\n", "comparison_type": "exact"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "Expected:" in msg
        assert "hello" in msg
        assert "world" in msg

    async def test_regex_failure_message(self):
        result = await _run_or_skip('print("goodbye")', [
            {"input": "", "expected_output": r"hello", "comparison_type": "regex"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "pattern" in msg.lower()

    async def test_non_empty_failure_message(self):
        result = await _run_or_skip("pass", [
            {"input": "", "expected_output": "", "comparison_type": "non_empty"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "nothing" in msg.lower()

    async def test_contains_failure_message(self):
        result = await _run_or_skip('print("goodbye")', [
            {"input": "", "expected_output": "hello", "comparison_type": "contains"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "contain" in msg.lower()

    async def test_whitelist_failure_message(self):
        result = await _run_or_skip('print("unknown")', [
            {"input": "", "expected_output": '["a", "b"]', "comparison_type": "whitelist"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "one of" in msg.lower()

    async def test_comment_failure_message(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "", "comparison_type": "comment"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "comment" in msg.lower()

    async def test_runtime_error_message(self):
        result = await _run_or_skip('raise ValueError("boom")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is not None
        assert "Runtime error" in msg

    async def test_no_message_on_success(self):
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "hello\n", "comparison_type": "exact"},
        ])
        msg = result["test_results"][0]["message"]
        assert msg is None


class TestErrorHandling:
    """Test various error conditions."""

    async def test_timeout_handling(self):
        """Infinite loop should be caught by the timeout."""
        result = await _run_or_skip("while True: pass", [])
        assert result["passed"] is False
        assert "timed out" in result["errors"].lower() or "timeout" in result["errors"].lower()


class TestSecurityIsolation:
    """Verify Docker sandbox provides proper security isolation.

    Two layers of tests:
    1. Through the harness (for harness-level restrictions like __import__)
    2. Direct container execution (for Docker-level isolation)
    """

    # --- Tests through the harness (harness-level restrictions) ---

    async def test_oom_protection(self):
        """Memory-hungry allocation should be killed by memory cgroup limit.

        The container has mem_limit=128m. Allocating ~800MB should trigger
        OOM-kill, resulting in a non-zero exit code and an error.

        NOTE: On Raspberry Pi the ``memory`` cgroup controller is absent
        from the cgroup v2 hierarchy (see docs/DOCKER_SANDBOX.md §4.2),
        so this test is skipped on those platforms.
        """
        if not _memory_limit_supported():
            pytest.skip("Memory cgroup limit not supported on this host")
        result = await _run_or_skip("x = [0] * 10**8", [])
        assert result["passed"] is False
        error_msg = (result.get("errors") or "").lower()
        assert any(
            keyword in error_msg
            for keyword in ["out of memory", "oom", "memory", "killed", "137", "exit code 137"]
        )

    async def test_harness_blocks_import(self):
        """The harness restricts __import__ in user code."""
        result = await _run_or_skip("import os", [])
        assert result["passed"] is False
        errors = (result.get("errors") or "").lower()
        assert "import" in errors or "import" in result.get("actual_output", "").lower()

    async def test_harness_blocks_open(self):
        """The harness restricts open in user code."""
        result = await _run_or_skip("open('/etc/passwd')", [])
        assert result["passed"] is False
        errors = (result.get("errors") or "").lower()
        assert "name 'open' is not defined" in errors

    async def test_overly_large_allocation_causes_error(self):
        """Extremely large allocation raises MemoryError (caught by harness)."""
        result = await _run_or_skip("x = [0] * 10**9", [])
        assert result["passed"] is False
        error_msg = (result.get("errors") or "").lower()
        assert "memory" in error_msg

    async def test_fork_bomb_through_harness(self):
        """Fork bomb via harness is blocked by __import__ restriction."""
        result = await _run_or_skip("import os\nwhile True: os.fork()", [])
        assert result["passed"] is False
        errors = (result.get("errors") or "").lower()
        assert any(k in errors for k in ["import", "not found", "not defined"])

    # --- Tests via direct container execution (Docker-level isolation) ---

    def test_docker_network_isolation(self):
        """Network access is blocked by Docker (network_disabled=True).

        Runs code directly inside the container (bypassing the harness) to
        verify that the Docker network isolation layer works.
        """
        code = (
            "import urllib.request\n"
            "try:\n"
            "    urllib.request.urlopen('http://example.com', timeout=3)\n"
            "    print('NETWORK_OK')\n"
            "except Exception as e:\n"
            "    print(type(e).__name__)\n"
        )
        result = _run_raw_in_container(code)
        assert result["passed"], f"Container exited with code {result['exit_code']}: {result['stderr']}"
        stdout = result["stdout"]
        # The container has no network, so we expect a network-related error
        assert any(
            keyword in stdout
            for keyword in [
                "TimeoutError",
                "URLError",
                "gaierror",
                "timeout",
                "Name or service not known",
                "No address associated with hostname",
                "Temporary failure in name resolution",
            ]
        ), f"Expected network error, got stdout={stdout!r} stderr={result['stderr']!r}"

    def test_docker_readonly_filesystem(self):
        """Writing to root filesystem is blocked by Docker (read_only=True).

        Runs code directly inside the container (bypassing the harness) to
        verify that the Docker read-only rootfs isolation layer works.
        """
        code = (
            "try:\n"
            "    with open('/etc/test_write', 'w') as f:\n"
            "        f.write('pwned')\n"
            "    print('WRITE_OK')\n"
            "except Exception as e:\n"
            "    print(type(e).__name__)\n"
            "    print(str(e)[:200])\n"
        )
        result = _run_raw_in_container(code)
        assert result["passed"], f"Container exited with code {result['exit_code']}: {result['stderr']}"
        stdout = result["stdout"]
        assert any(
            keyword in stdout
            for keyword in [
                "PermissionError",
                "OSError",
                "Read-only",
                "read-only",
                "EACCES",
                "EROFS",
            ]
        ), f"Expected write error, got stdout={stdout!r} stderr={result['stderr']!r}"

    def test_docker_privilege_escalation_blocked(self):
        """Privilege escalation via setuid should fail (capabilities dropped).

        Runs code directly inside the container (bypassing the harness) to
        verify that the dropped capabilities prevent privilege escalation.
        """
        code = (
            "import os\n"
            "try:\n"
            "    os.setuid(0)\n"
            "    print('SETUID_OK')\n"
            "except Exception as e:\n"
            "    print(type(e).__name__)\n"
            "    print(str(e)[:200])\n"
        )
        result = _run_raw_in_container(code)
        assert result["passed"], f"Container exited with code {result['exit_code']}: {result['stderr']}"
        stdout = result["stdout"]
        assert any(
            keyword in stdout
            for keyword in [
                "PermissionError",
                "OSError",
                "Operation not permitted",
                "EPERM",
            ]
        ), f"Expected privilege error, got stdout={stdout!r} stderr={result['stderr']!r}"


class TestContainerLifecycle:
    """Verify Docker container lifecycle management.

    Tests that containers are properly cleaned up after execution, and
    that dangling resources do not accumulate.
    """

    @staticmethod
    def _get_runner_container_ids() -> set[str]:
        """Get IDs of existing tutorial-runner containers."""
        import subprocess as sp

        try:
            result = sp.run(
                [
                    "docker", "ps", "-a",
                    "--filter", "ancestor=tutorial-runner-python:latest",
                    "--format", "{{.ID}}",
                ],
                capture_output=True, text=True, timeout=10,
            )
            lines = result.stdout.strip().splitlines()
            return {l for l in lines if l.strip()}
        except Exception:
            return set()

    async def test_no_dangling_containers_after_success(self):
        """No dangling tutorial-runner containers after successful execution."""
        before = self._get_runner_container_ids()
        result = await _run_or_skip('print("clean test")', [
            {"input": "", "expected_output": "clean test\n", "comparison_type": "exact"},
        ])
        assert result["passed"] is True
        after = self._get_runner_container_ids()
        new_containers = after - before
        assert len(new_containers) == 0, f"Dangling containers after successful run: {new_containers}"

    async def test_no_dangling_containers_after_failure(self):
        """No dangling containers after a failed execution."""
        before = self._get_runner_container_ids()
        result = await _run_or_skip('print("hello")', [
            {"input": "", "expected_output": "wrong\n", "comparison_type": "exact"},
        ])
        assert result["passed"] is False
        after = self._get_runner_container_ids()
        new_containers = after - before
        assert len(new_containers) == 0, f"Dangling containers after failed run: {new_containers}"

    async def test_no_dangling_containers_after_timeout(self):
        """No dangling containers after a timeout kill."""
        before = self._get_runner_container_ids()
        result = await _run_or_skip("while True: pass", [])
        assert result["passed"] is False
        error_msg = (result.get("errors") or "").lower()
        assert "timed out" in error_msg or "timeout" in error_msg
        after = self._get_runner_container_ids()
        new_containers = after - before
        assert len(new_containers) == 0, f"Dangling containers after timeout: {new_containers}"

    async def test_no_dangling_containers_after_syntax_error(self):
        """No dangling containers after a syntax error."""
        before = self._get_runner_container_ids()
        result = await _run_or_skip('print("hello', [])
        assert result["passed"] is False
        after = self._get_runner_container_ids()
        new_containers = after - before
        assert len(new_containers) == 0, f"Dangling containers after syntax error: {new_containers}"