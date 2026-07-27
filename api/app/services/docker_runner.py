"""
Docker-based sandbox runner for user-submitted code.

Provides the DockerRunner class that executes user code inside Docker containers
with strict resource limits and security constraints. Offloads synchronous
Docker SDK calls to a thread pool executor so the FastAPI event loop is never
blocked.

Uses ``put_archive`` to deliver the harness script to the container (avoiding
volume mount path-resolution issues when the app itself runs in Docker / DinD
environments). See https://docker-py.readthedocs.io/ for the SDK reference.

On timeout, the container is force-killed to prevent dangling resources.

A ``warm_up()`` method is provided to prime the Docker daemon (overlay
filesystem, cgroups) on application startup, avoiding first-submission
timeouts caused by cold-start overhead on resource-constrained hosts
such as the Raspberry Pi.
"""

import asyncio
import io
import json
import logging
import tarfile
from pathlib import Path
from typing import Dict, List, Optional

import requests

from app.config import (
    DOCKER_ENABLED,
    DOCKER_LANGUAGES_CONFIG,
    MAX_OUTPUT_CHARS,
)


logger = logging.getLogger(__name__)


class DockerUnavailableError(Exception):
    """Raised when the Docker daemon is not reachable or not installed."""


class LanguageConfigError(Exception):
    """Raised when the language configuration is invalid or missing."""


def _render_harness(
    user_code: str, test_cases: list[dict], test_suite: str | None = None
) -> str:
    """Render the harness template with user code and test cases.

    Reads the Jinja2-style template from the harness file and substitutes
    the {user_code!r} and {test_cases!r} placeholders with repr() output
    so the rendered script is valid Python.
    """
    harness_path = (
        Path(__file__).resolve().parent.parent.parent
        / "docker"
        / "harnesses"
        / "python_harness.py.j2"
    )
    if not harness_path.exists():
        raise FileNotFoundError(f"Harness template not found at {harness_path}")
    template = harness_path.read_text()
    return template.replace("{user_code!r}", repr(user_code)).replace(
        "{test_cases!r}", repr(test_cases)
    )


def _load_languages_config(config_path: str | Path) -> dict:
    """Load language configuration from JSON file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Languages config not found at {path}")
    return json.loads(path.read_text())


def _truncate_output(result: dict) -> dict:
    """Truncate long string fields in the result dict."""
    for key in ("actual_output", "expected_output", "errors"):
        if isinstance(result.get(key), str) and len(result[key]) > MAX_OUTPUT_CHARS:
            result[key] = result[key][:MAX_OUTPUT_CHARS] + "... (truncated)"
    for tr in result.get("test_results", []):
        for key in ("actual_output", "expected_output", "errors"):
            if isinstance(tr.get(key), str) and len(tr[key]) > MAX_OUTPUT_CHARS:
                tr[key] = tr[key][:MAX_OUTPUT_CHARS] + "... (truncated)"
    return result


def _get_container_logs(container) -> bytes:
    """Safely retrieve container logs, returning empty bytes on failure.

    The Docker API can return 409 Conflict when a container exits and its
    state transitions to 'dead' or 'removed' between ``wait()`` and
    ``logs()``. This helper prevents that race condition from propagating
    as an unhandled exception.
    """
    try:
        return container.logs(stdout=True, stderr=True)
    except Exception:
        return b""


def _remove_container_with_retry(container, max_attempts: int = 5):
    """Remove a container with retry + backoff for Docker daemon races.

    On ARM/Pi the Docker daemon sometimes returns "removal of container
    ... is already in progress" when a container transitions between
    states.  Retrying after a short delay resolves the issue.

    Falls back to ``docker rm -f`` via subprocess as a last resort,
    because the Docker SDK's ``remove(force=True)`` can get stuck on
    state transitions on this platform.
    """
    import subprocess as sp
    import time

    cid = ""
    try:
        cid = container.id
    except Exception:
        return

    # Step 1: Ensure the container is stopped (kill if running).
    # remove(force=True) should do this atomically, but on some
    # platforms the SDK's force-remove times out on running containers.
    try:
        container.kill()
    except Exception:
        pass  # Already stopped or inaccessible — proceed to remove

    # Step 2: Try SDK remove with retry
    for attempt in range(max_attempts):
        try:
            container.remove(force=True)
            return
        except Exception:
            if attempt < max_attempts - 1:
                time.sleep(0.5 * (attempt + 1))

    # Step 3: Last resort: use Docker CLI directly
    if cid:
        try:
            sp.run(
                ["docker", "rm", "-f", cid],
                capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass

    # Step 4: Fallback: hard-kill via CLI if still present
    try:
        remaining = sp.run(
            ["docker", "ps", "-a", "-q", "--filter", f"id={cid}"],
            capture_output=True, text=True, timeout=5,
        )
        if remaining.stdout.strip():
            # Container still exists — one more hard kill
            sp.run(
                ["docker", "rm", "-f", cid],
                capture_output=True, text=True, timeout=10,
            )
            # Final check
            remaining = sp.run(
                ["docker", "ps", "-a", "-q", "--filter", f"id={cid}"],
                capture_output=True, text=True, timeout=5,
            )
            if remaining.stdout.strip():
                logger.warning(
                    "Container %s still present after all removal attempts",
                    cid[:12],
                )
            else:
                logger.info(
                    "Container %s removed via docker CLI fallback", cid[:12]
                )
        else:
            logger.info("Container %s already removed", cid[:12])
    except Exception:
        pass


class DockerRunner:
    """Runs user code in Docker containers with sandbox isolation.

    Uses the Docker Python SDK to create ephemeral containers with strict
    resource limits. Supports multiple languages via a language config JSON.

    The class is designed to be a singleton at the module level so the Docker
    client is reused across requests.
    """

    def __init__(self, languages_config_path: Optional[str | Path] = None):
        if languages_config_path is None:
            languages_config_path = DOCKER_LANGUAGES_CONFIG
        self._client = None
        self.languages: dict = {}
        self._warmed_up: bool = False
        self._load_config(languages_config_path)

    @property
    def client(self):
        """Lazy-initialized Docker client (reused across calls)."""
        if self._client is None:
            try:
                import docker

                self._client = docker.from_env()
                # Test connection
                self._client.ping()
                # Check if memory limits are actually supported.
                # On Raspberry Pi the 'memory' cgroup controller is often
                # unavailable, so mem_limit is silently ignored.
                info = self._client.info()
                if not info.get("MemoryLimit", True):
                    logger.warning(
                        "Docker memory limit support is NOT available on this host. "
                        "The 'memory' cgroup controller is missing from the cgroup v2 "
                        "hierarchy. The mem_limit setting will be silently ignored. "
                        "CPU and PIDs limits are unaffected."
                    )

                # Clean orphaned runner containers from previous crashed runs
                self._clean_orphans()
            except Exception as e:
                self._client = None
                logger.warning(
                    "Docker daemon unreachable: %s. "
                    "Falling back to subprocess-based runner.",
                    e,
                )
                raise DockerUnavailableError(
                    f"Docker daemon unreachable: {e}"
                ) from e
        return self._client

    def _clean_orphans(self):
        """Remove runner containers stuck in 'created' state from crashed runs.

        When the API server shuts down unexpectedly (e.g. container restart,
        process kill), any in-flight ``container.create()`` calls leave the
        container in 'created' state with no cleanup.
        """
        cleaned = 0
        for lang, cfg in self.languages.items():
            image = cfg.get("image", "")
            if not image:
                continue
            try:
                orphans = self.client.containers.list(
                    all=True,
                    filters={"ancestor": image, "status": "created"},
                )
                for c in orphans:
                    try:
                        c.remove(force=True)
                        logger.info(
                            "Cleaned orphaned runner container %s (image: %s)",
                            c.id[:12], image,
                        )
                        cleaned += 1
                    except Exception:
                        logger.warning(
                            "Failed to remove orphaned container %s", c.id[:12],
                        )
            except Exception as exc:
                logger.debug("Orphan cleanup for '%s' skipped: %s", image, exc)
        if cleaned:
            logger.info("Startup: cleaned %d orphaned runner container(s)", cleaned)

    def _load_config(self, config_path: str | Path):
        """Load and validate language configuration."""
        raw = _load_languages_config(config_path)
        self.languages = {}
        for lang, cfg in raw.items():
            required = {
                "image",
                "extension",
                "run_command",
                "memory_limit",
                "cpu_limit",
                "pids_limit",
                "timeout_seconds",
            }
            missing = required - set(cfg.keys())
            if missing:
                raise LanguageConfigError(
                    f"Language '{lang}' missing required config keys: {missing}"
                )
            self.languages[lang] = cfg

    def get_config(self, language: str) -> dict:
        """Get configuration for a language, raising if not found."""
        cfg = self.languages.get(language)
        if cfg is None:
            raise LanguageConfigError(
                f"Unsupported language: '{language}'. "
                f"Supported: {', '.join(sorted(self.languages.keys()))}"
            )
        return cfg


    async def warm_up(self):
        """Prime the Docker daemon for faster first-submission response.

        For each configured language, this method:
        1. Ensures the Docker image is available locally (pulls if needed)
        2. Creates and runs a throwaway container that exits immediately
        3. Removes the container

        This initializes overlay filesystem layers, cgroup controllers,
        and process-scheduling infrastructure so real user submissions
        don't hit cold-start latency on the first attempt.

        The method is safe to call multiple times -- subsequent calls are
        no-ops after the first successful warm-up.
        """
        if self._warmed_up or self._client is None:
            return

        logger.info("Warming up Docker sandbox runner ...")

        for lang, cfg in self.languages.items():
            image = cfg.get("image", "")
            if not image:
                continue

            container = None
            try:
                # Step 1: Ensure the image is available locally.
                # ``pull()`` is a fast no-op when the image is already cached,
                # but forces Docker to resolve the image manifest and prime
                # the layer cache. This avoids ImageNotFound errors on the
                # very first container create() call.
                logger.info("Warm-up: ensuring image '%s' is available ...", image)
                self.client.images.pull(image)
                logger.info("Warm-up: image '%s' ready", image)

                # Step 2: Create a minimal throwaway container that exits
                # immediately. This primes overlay filesystem initialization,
                # cgroup creation, and process-startup overhead so that real
                # submissions don't pay this latency tax.
                logger.info("Warm-up: creating throwaway container for '%s' ...", image)
                container = self.client.containers.create(
                    image=image,
                    command=cfg.get("run_command", ["python3", "-c", "print('warm-up')"]),
                    network_disabled=True,
                    read_only=False,
                    mem_limit=cfg.get("memory_limit", "64m"),
                    nano_cpus=cfg.get("cpu_limit", 250000000),
                    pids_limit=cfg.get("pids_limit", 50),
                    user="sandbox",
                    cap_drop=["ALL"],
                )

                # Inject a minimal harness that just prints OK and exits,
                # so we don't need the full harness template.
                warmup_script = (
                    '#!/usr/bin/env python3\n'
                    'import json\n'
                    "result = {'passed': True, 'actual_output': 'warm-up\\n', "
                    "'expected_output': '', 'errors': '', 'test_results': []}\n"
                    'print(json.dumps(result))\n'
                )
                self._inject_harness(container, warmup_script)

                # Start and wait with a generous timeout (warm-up itself can
                # be slow on cold Docker on ARM).
                logger.info("Warm-up: starting throwaway container ...")
                container.start()
                container.wait(timeout=30)
                logger.info(
                    "Warm-up: container for '%s' completed successfully", image
                )

            except Exception as exc:
                logger.warning(
                    "Warm-up: failed for image '%s': %s (non-fatal)", image, exc
                )
            finally:
                # Always clean up the warm-up container
                try:
                    if container is not None:
                        _remove_container_with_retry(container)
                except Exception:
                    pass

        self._warmed_up = True
        logger.info("Docker sandbox runner warm-up complete")

    def _inject_harness(self, container, harness_script: str):
        """Inject a harness script into a container via put_archive.

        Builds a tar archive containing the harness file and uses the Docker
        API's put_archive() to copy it to /tmp/runner/ inside the container.
        """
        harness_filename = "runner.py"
        tar_entry = f"runner/{harness_filename}"
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            file_info = tarfile.TarInfo(name=tar_entry)
            script_bytes = harness_script.encode("utf-8")
            file_info.size = len(script_bytes)
            file_info.mode = 0o644
            tar.addfile(file_info, io.BytesIO(script_bytes))
        tar_buffer.seek(0)
        tar_data = tar_buffer.getvalue()
        container.put_archive(path="/tmp", data=tar_data)



    async def run_code(
        self,
        user_code: str,
        test_cases: list[dict],
        language: str = "python",
    ) -> dict:
        """Run user code inside a Docker container.

        Uses container.create() + put_archive() + start() instead of volume
        mounts so it works correctly when the API runs inside a Docker
        container (Docker-in-Docker path resolution issue).

        Args:
            user_code: The user's source code as a string.
            test_cases: List of test case dicts with keys: input, expected_output,
                       comparison_type, name (optional).
            language: Language key from the config (default: "python").

        Returns:
            Dict with keys: passed, actual_output, expected_output, errors, test_results.
            Same schema as the current exercise_runner.run_code().
        """
        cfg = self.get_config(language)

        # Render the harness script
        harness_script = _render_harness(user_code, test_cases)

        try:
            # Run container synchronously in a thread pool.
            # The timeout is enforced BOTH inside the thread (container.wait timeout)
            # AND at the asyncio level (safety net). On timeout the container is
            # force-killed before the result dict is returned.
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self._run_container, cfg, harness_script
                ),
                timeout=cfg["timeout_seconds"] + 10,
            )
            return _truncate_output(result)
        except asyncio.TimeoutError:
            return {
                "passed": False,
                "actual_output": "",
                "expected_output": "",
                "errors": "Execution timed out",
                "test_results": [],
            }
        except DockerUnavailableError:
            raise  # Re-raise for the caller to handle fallback
        except Exception as e:
            logger.error(
                "Docker runner unexpected error: %s: %s. "
                "Raising exception for subprocess fallback.",
                type(e).__name__,
                e,
            )
            raise

    def _run_container(self, cfg: dict, harness_script: str) -> dict:
        """Synchronous container execution in a thread pool.

        Uses put_archive() to copy the harness script into the container
        filesystem instead of a host-volume bind mount. This solves the
        Docker-in-Docker path mismatch that occurs when the API runs inside
        a container (the Docker daemon on the host can't resolve paths that
        only exist inside the API container).

        The harness is written via the Docker API to /tmp/runner/runner.py
        on the container's overlay layer before the container starts. No
        tmpfs is mounted on /tmp because that would hide the injected file;
        the ephemeral overlay layer provides sufficient isolation (container
        is auto-removed after use, runs as non-root, has no capabilities,
        and no network access).
        """
        harness_filename = cfg.get("harness_filename", "runner.py")
        # put_archive(path="/tmp", data=tar) extracts the tar into /tmp,
        # so the tar entry "runner/runner.py" lands at /tmp/runner/runner.py.
        # Docker's API creates parent directories automatically.
        tar_entry = f"runner/{harness_filename}"

        # Build a tar archive containing the harness file
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            file_info = tarfile.TarInfo(name=tar_entry)
            script_bytes = harness_script.encode("utf-8")
            file_info.size = len(script_bytes)
            file_info.mode = 0o644
            tar.addfile(file_info, io.BytesIO(script_bytes))
        tar_buffer.seek(0)
        tar_data = tar_buffer.getvalue()

        import docker as docker_sdk

        try:
            # Step 1: Create container (stopped) — no volume mounts.
            # No tmpfs on /tmp so the put_archive files survive into runtime.
            container = self.client.containers.create(
                image=cfg["image"],
                command=cfg["run_command"],
                network_disabled=True,
                read_only=False,  # Required for put_archive (filesystem write)
                mem_limit=cfg["memory_limit"],
                nano_cpus=cfg["cpu_limit"],
                pids_limit=cfg["pids_limit"],
                user="sandbox",
                cap_drop=["ALL"],
            )
        except docker_sdk.errors.ImageNotFound:
            return {
                "passed": False,
                "actual_output": "",
                "expected_output": "",
                "errors": (
                    f"Docker image '{cfg['image']}' not found. "
                    "Run 'api/docker/build_images.sh' to build it."
                ),
                "test_results": [],
            }
        except docker_sdk.errors.APIError as e:
            if "Out of memory" in str(e) or "137" in str(e):
                return {
                    "passed": False,
                    "actual_output": "",
                    "expected_output": "",
                    "errors": "Out of memory",
                    "test_results": [],
                }
            raise

        try:
            # Step 2: Copy harness file into the container via Docker API.
            # put_archive on a stopped container writes to the overlay layer.
            # Docker creates parent directories (runner/) inside /tmp
            # automatically, so the file lands at /tmp/runner/runner.py.
            try:
                container.put_archive(path="/tmp", data=tar_data)
            except docker_sdk.errors.APIError:
                raise DockerUnavailableError(
                    "Failed to copy harness into sandbox container"
                )

            # Step 3: Start the container — /tmp is the overlay's /tmp (not
            # tmpfs), so /tmp/runner/runner.py is visible to the process.
            try:
                container.start()
            except docker_sdk.errors.APIError as e:
                raise DockerUnavailableError(
                    f"Failed to start sandbox container: {e}"
                )

            # Verify the container actually transitioned to 'running'.
            # On some platforms (ARM / resource-constrained hosts) the
            # start() call can return without the container transitioning,
            # leaving it stuck in 'created' state.  A quick reload detects
            # this so we can fail fast instead of waiting for a timeout.
            container.reload()
            if container.status == "created":
                logger.warning(
                    "Container %s stayed in 'created' state after start() — "
                    "failing fast instead of hanging on wait()",
                    container.id[:12],
                )
                raise DockerUnavailableError(
                    "Sandbox container failed to transition to 'running' state"
                )

            # Step 4: Wait for completion with Docker-level timeout
            try:
                container.wait(timeout=cfg["timeout_seconds"])
                logs_bytes = _get_container_logs(container)
            except (requests.ReadTimeout, requests.ConnectionError):
                # Container did not finish within the timeout.
                # The finally block handles kill + removal atomically.
                logs_bytes = _get_container_logs(container)
                parsed = self._parse_container_output(logs_bytes)
                return {
                    "passed": False,
                    "actual_output": parsed.get("actual_output", ""),
                    "expected_output": "",
                    "errors": "Execution timed out",
                    "test_results": [],
                }
            except docker_sdk.errors.APIError as e:
                # Some API errors are also timeout-like
                logs_bytes = _get_container_logs(container)
                parsed = self._parse_container_output(logs_bytes)
                return {
                    "passed": False,
                    "actual_output": parsed.get("actual_output", ""),
                    "expected_output": "",
                    "errors": f"Docker API error: {e}",
                    "test_results": [],
                }
        finally:
            # Best-effort: remove(force=True) atomically kills + removes.
            # Single removal point — avoids "already in progress" 409 races.
            _remove_container_with_retry(container)

        return self._parse_container_output(logs_bytes)

    def _parse_container_output(self, logs_bytes: bytes) -> dict:
        """Parse container logs bytes into the standard result dict.

        The harness prints a JSON line to stdout which we parse.
        If parsing fails, fall back to raw output.

        Raises DockerUnavailableError when the raw output indicates a Docker
        sandbox infrastructure failure (e.g. the harness file was not
        injected, Python bootstrap failed) rather than a user-code error.
        This allows the caller to fall through to the subprocess runner.
        """
        if isinstance(logs_bytes, bytes):
            output = logs_bytes.decode("utf-8", errors="replace")
        else:
            output = str(logs_bytes)

        lines = [l.strip() for l in output.strip().split("\n") if l.strip()]
        if not lines:
            return {
                "passed": False,
                "actual_output": "",
                "expected_output": "",
                "errors": "No output from container",
                "test_results": [],
            }

        first_line = lines[0]
        try:
            result = json.loads(first_line)
            return result
        except (json.JSONDecodeError, TypeError):
            # Check for Docker infrastructure failure patterns.
            # These indicate the sandbox container itself failed to bootstrap
            # (e.g. harness file not injected, Python not found, missing
            # dependencies) rather than user code producing bad output.
            infra_errors = (
                "can't open file",
                "No such file or directory",
                "ModuleNotFoundError",
                "ImportError",
            )
            if any(pattern in first_line for pattern in infra_errors):
                raise DockerUnavailableError(
                    f"Docker sandbox infrastructure failure: {first_line}"
                )

            return {
                "passed": False,
                "actual_output": first_line,
                "expected_output": "",
                "errors": "\n".join(lines[1:]) if len(lines) > 1 else "Failed to parse runner output",
                "test_results": [],
            }


# Module-level singleton — reuse Docker client across requests
_runner: Optional[DockerRunner] = None


def get_runner() -> DockerRunner:
    """Get or create the singleton DockerRunner instance."""
    global _runner
    if _runner is None and DOCKER_ENABLED:
        _runner = DockerRunner()
    return _runner


async def run_code_in_docker(
    user_code: str,
    test_cases: list[dict],
    language: str = "python",
) -> dict:
    """Convenience async function to run code in Docker.

    Uses the singleton DockerRunner. Returns same dict schema as
    exercise_runner.run_code(). Raises DockerUnavailableError if
    Docker is not available.

    Args:
        user_code: The user's source code.
        test_cases: List of test case dicts.
        language: Language key (default: "python").

    Returns:
        Dict with keys: passed, actual_output, expected_output, errors, test_results.
    """
    runner = get_runner()
    if runner is None:
        raise DockerUnavailableError(
            "Docker runner is not enabled (DOCKER_ENABLED=False)"
        )
    return await runner.run_code(user_code, test_cases, language)
