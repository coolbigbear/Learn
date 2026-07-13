# Docker Sandbox — Architecture & Design

## 1. Motivation

Replace the current subprocess-based sandbox (`exercise_runner.py`) with Docker
container isolation for running user-submitted code.

| Dimension | Current (subprocess) | Target (Docker) |
|-----------|----------------------|-----------------|
| Security  | `resource.setrlimit` + restricted builtins — easily bypassed | True container isolation, seccomp, no-network, read-only rootfs |
| Languages | Python only | Language-agnostic — Python, JavaScript, Go, etc. |
| Resource limits | CPU/Memory via `setrlimit` | cgroups (CPU, memory, pids, disk) |
| Filesystem | Tempdir, cleaned after run | Read-only rootfs, isolated /tmp |
| Network | Full host network | No network by default |
| Cleanup | Manual tmpdir removal | Container + volume auto-removed |

## 2. System Overview

```
┌──────────────────────┐      ┌─────────────────────────────┐
│   FastAPI Server     │      │   Docker Engine             │
│                      │      │                             │
│   exercise_runner.py │──────►   tutorial-runner-python    │
│   ─────────────────  │ SDK  │   (container)               │
│   docker_runner.py   │      │   - read-only rootfs        │
│                      │      │   - --network none          │
│   Router calls       │      │   - --memory 128m           │
│   docker_runner      │      │   - --cpus 0.5              │
│   .run_code(...)     │      │   - --pids-limit 50         │
│                      │      │   - non-root sandbox user   │
│                      │      │   - seccomp default         │
└──────────────────────┘      └─────────────────────────────┘
```

The FastAPI server communicates with Docker via the **Docker SDK for Python**
(`docker` package) over the local Docker socket. No HTTP gateway or sidecar.

### 2.1 Execution Flow

```
User submits code (POST /api/exercises/{id}/run)
    │
    ▼
Router (exercises.py) calls docker_runner.run_code(code, test_cases, language)
    │
    ▼
DockerRunner:
  1. Load language config      → image name, extension, run command
  2. Generate harness script    → writes to tempdir
  3. docker.containers.run(
       image=tutorial-runner-python,
       command=["python3", "/tmp/runner/runner.py"],
       volumes={tmpdir: {"bind": "/tmp/runner", "mode": "ro"}},
       network_disabled=True,
       read_only=True,
       mem_limit="128m",
       nano_cpus=500_000_000,
       pids_limit=50,
       user="sandbox",
       remove=True,
       detach=False,
     )
  4. Parse stdout as JSON
  5. Return RunResult dict (same schema as current)
```

## 3. Container Image Design

### 3.1 Image Registry

All images are built locally (no registry push needed for MVP).

| Language   | Image Tag                      | Base Image          | In-MVP |
|-----------|--------------------------------|---------------------|--------|
| Python    | `tutorial-runner-python:latest`| `python:3.11-slim`  | ✅     |
| JavaScript| `tutorial-runner-node:latest`  | `node:20-slim`      | ❌     |
| Go        | `tutorial-runner-go:latest`    | `golang:1.22`       | ❌     |

### 3.2 Python Image (MVP)

```dockerfile
# api/docker/images/python/Dockerfile
FROM python:3.11-slim

# Create non-root sandbox user
RUN addgroup --system --gid 1001 sandbox \
    && adduser --system --uid 1001 --ingroup sandbox --disabled-password --no-create-home sandbox

# No Python packages needed — all execution is stdlib-only
USER sandbox
WORKDIR /home/sandbox

# Verify nothing runs as root
RUN python3 -c "import os; assert os.geteuid() != 0, 'Must not run as root'"
```

**Key points:**
- No pip packages — user code only uses stdlib (same restriction as current runner)
- Non-root user `sandbox` (UID 1001)
- No entrypoint — the command is provided at runtime
- Image is ~120 MB compressed

### 3.3 Future Language Image Template

Each language image follows the same pattern:
1. Start from official slim image
2. Create `sandbox` non-root user
3. No entrypoint (command injected at runtime)
4. No network tools, no build tools, no dev packages
5. Verify non-root assertion at build time

## 4. Security Model

| Control | Implementation | Rationale |
|---------|---------------|-----------|
| **Read-only rootfs** | `read_only=True` in Docker SDK | Container cannot modify its own filesystem |
| **Writable /tmp** | `tmpfs=/tmp:size=10M,noexec,nosuid,uid=1001,gid=1001` | Temp storage for user code without giving write access to rootfs |
| **No network** | `network_disabled=True` | Prevents data exfiltration, network attacks, external calls |
| **Non-root user** | `user="sandbox"` (UID 1001) | Container processes can't escalate to root |
|| **Memory limit** | `mem_limit="128m"` | cgroup memory.max — OOM-kills runaway processes. **NOTE:** Not enforced on Raspberry Pi — see §4.2. |
|| **CPU limit** | `nano_cpus=500_000_000` (0.5 CPU) | Prevents CPU-starving the host |
| **Process limit** | `pids_limit=50` | Prevents fork bombs |
| **Seccomp** | Docker default profile (auto) | Blocks ~44 dangerous syscalls (no `mount`, `ptrace`, `bpf`, etc.) |
| **No privileged** | `privileged=False` (default) | Container cannot access host devices |
| **No capabilities** | `cap_drop=[["ALL"]]` | Drops all Linux capabilities |
| **Container timeout** | Async timer + `container.kill()` at 5s | Prevents infinite loops from consuming resources |
| **Auto-cleanup** | `auto_remove=True` | Container is removed on exit |
| **Volume mode** | Bind mount with `mode="ro"` | Code is injected read-only into the container |
| **No --pid=host** | Default (isolated PID namespace) | Container can't see host processes |

### 4.1 Security Constraints Not Yet Applied

These Docker features require runtime configuration or kernel tuning and are
deferred to a hardening phase:

- **AppArmor/SELinux**: Not pre-installed on Raspberry Pi OS. Would add
  mandatory access control for the container process.
- **No-new-privileges**: `security_opt=["no-new-privileges:true"]` — prevents
  `setuid` escalation inside the container. Add in hardening pass.
- **Read-only /proc and /sys**: Requires custom seccomp profile. Add if
  container escape is demonstrated in penetration testing.
- **User namespaces** (`--userns-remap`): Maps container root to unprivileged
  host UID. Significantly harder to debug; defer to production hardening.

### 4.2 Platform Limitations — Raspberry Pi

The Raspberry Pi kernel and Debian Trixie userland on this system **do not** include
the `memory` cgroup controller in the cgroup v2 hierarchy:

```
$ cat /sys/fs/cgroup/cgroup.controllers
cpuset cpu io pids
```

This means:
- `--memory` / `mem_limit` flags are silently ignored by Docker
- The `docker info` output reports `MemoryLimit: false` and `WARNING: No memory limit support`
- Containers can allocate unlimited host memory (OOM-killer will not fire on the container)
- The `mem_limit` fields in `languages.json` and `config.py` are **decorative** on this platform

**What still works:**
- CPU limits (`nano_cpus`) — enforced via `cpu` cgroup controller ✅
- PIDs limits (`pids_limit`) — enforced via `pids` cgroup controller ✅
- Read-only rootfs, no-network, non-root user, seccomp, capability drops — all
  independent of cgroup memory controller ✅
- Container timeout and force-kill — enforced at the Docker SDK level ✅

The Docker sandbox is fully functional for educational use on RPi. The only
missing control is RAM capping, which is acceptable for a learning platform
where student code is trusted and short-lived.

## 5. Language Configuration

Languages are configured via a JSON file at `api/docker/languages.json`:

```json
{
  "python": {
    "image": "tutorial-runner-python:latest",
    "extension": ".py",
    "run_command": ["python3", "/tmp/runner/runner.py"],
    "harness_template": "python_harness.py.j2",
    "memory_limit": "128m",
    "cpu_limit": 500000000,
    "pids_limit": 50,
    "timeout_seconds": 5
  },
  "javascript": {
    "image": "tutorial-runner-node:latest",
    "extension": ".js",
    "run_command": ["node", "/tmp/runner/runner.js"],
    "harness_template": "node_harness.js.j2",
    "memory_limit": "256m",
    "cpu_limit": 500000000,
    "pids_limit": 50,
    "timeout_seconds": 5
  }
}
```

**Adding a new language requires:**
1. A Dockerfile under `api/docker/images/<lang>/Dockerfile`
2. An entry in `languages.json` with image tag, extension, run command, and harness template
3. A harness template under `api/docker/harnesses/<lang>_harness.*.j2`
4. Build the image: `docker build -t tutorial-runner-<lang> api/docker/images/<lang>/`

## 6. Harness Design

### 6.1 Python Harness

The Python harness is the **same** template that currently lives inside
`exercise_runner.py`. It is extracted to a standalone file at
`api/docker/harnesses/python_harness.py.j2` and rendered at container start time.

The harness handles all comparison types (exact, regex, non_empty, contains,
whitelist, comment, code_contains) identically to the current implementation.

No changes to the harness logic — the Docker runner only changes the execution
environment.

### 6.2 Language-Specific Harness for Future Languages

Each language harness follows the same contract:

1. Read JSON test cases from environment variable or a mounted file
2. Execute user code with test case input on stdin
3. Capture stdout/stderr
4. Compare output using the specified comparison_type
5. Print JSON to stdout with the same schema as current

```python
# Pseudocode contract (same for any language harness)
{
    "passed": bool,
    "actual_output": str,
    "expected_output": str,
    "errors": str | None,
    "test_results": [
        {
            "test_index": int,
            "passed": bool,
            "actual_output": str,
            "expected_output": str,
            "errors": str | None,
            "name": str | None,
            "message": str | None,
            "comparison_type": str
        }
    ]
}
```

## 7. API Contract — `DockerRunner`

### 7.1 Interface

```python
class DockerRunner:
    """Runs user code in Docker containers."""

    def __init__(self, languages_config_path: str | Path):
        self.client = docker.from_env()
        self.languages = self._load_config(languages_config_path)

    async def run_code(
        self,
        user_code: str,
        test_cases: list[dict],
        language: str = "python",
    ) -> dict:
        """Run user code and return the same dict schema as current run_code()."""
```

### 7.2 Input Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `user_code` | `str` | — | User-submitted source code |
| `test_cases` | `list[dict]` | `[]` | Test case objects with `input`, `expected_output`, `comparison_type` |
| `language` | `str` | `"python"` | Language key from `languages.json` |

### 7.3 Return Value

Returns the same dict schema as the current `run_code()`:

```python
{
    "passed": bool,          # All test cases passed
    "actual_output": str,    # First test case stdout
    "expected_output": str,  # First test case expected output
    "errors": str | None,    # Stderr or error message
    "test_results": [        # One per test case
        {
            "test_index": int,
            "passed": bool,
            "actual_output": str,
            "expected_output": str,
            "errors": str | None,
            "name": str | None,
            "message": str | None,
            "comparison_type": str,
        }
    ],
}
```

Truncation: all string fields are truncated to 10,000 chars per field (matching
current `MAX_OUTPUT_CHARS`).

### 7.4 Error States

| Condition | Behaviour |
|-----------|-----------|
| Container timeout | Kill container, return `{passed: false, errors: "Execution timed out"}` |
| Docker daemon unreachable | Raise `DockerUnavailableError` → 503 response |
| Unknown language | Raise `KeyError` / validation failure → 400 response |
| Image not found | Auto-build on first use (or raise actionable error) |
| User code syntax error | Captured by harness → `{passed: false, errors: "SyntaxError: ..."}` |
| Output too large | Truncated at MAX_OUTPUT_CHARS |
| Container OOM killed | Docker returns 137 exit code → `{passed: false, errors: "Out of memory"}` |

## 8. Container Lifecycle

```
1. PREPARE
   ├── Ensure image exists (build if missing)
   ├── Create tempdir on host
   ├── Render harness template → harness.py
   ├── Write user_code + test_cases into harness
   └── Write harness to tmpdir/runner.py

2. EXECUTE
   ├── docker.containers.run(
   │     image, command, volumes, network_disabled,
   │     read_only=True, tmpfs, mem_limit, nano_cpus,
   │     pids_limit, user, cap_drop, auto_remove=True,
   │     detach=False, stdout=True, stderr=True,
   │   )
   ├── Await completion (blocking call inside asyncio.get_event_loop().run_in_executor)
   └── On timeout: container.kill()

3. PARSE
   ├── Read container logs (stdout + stderr)
   ├── Parse first line of stdout as JSON
   ├── Apply truncation
   └── Return dict

4. CLEANUP
   ├── auto_remove=True handles container cleanup
   ├── Tempdir removed in finally block
   └── No dangling containers on success
```

**Timeout implementation:**

```python
try:
    result = await asyncio.wait_for(
        asyncio.get_event_loop().run_in_executor(None, self._run_sync, ...),
        timeout=timeout_seconds,
    )
except asyncio.TimeoutError:
    container.kill()  # force kill
    return timeout_error_dict()
```

The synchronous `_run_sync` method calls `client.containers.run(...)` which blocks
for container completion. This is offloaded to a thread pool executor so the
FastAPI event loop isn't blocked.

## 9. Migration Path

### Phase 1: Parallel deployment (this sprint)

1. Create Dockerfiles and build images
2. Create `docker_runner.py` with `DockerRunner` class
3. Create language config + harness template
4. Update `exercise_runner.py` — add a `ENABLE_DOCKER` flag
5. Update `exercises.py` router to use `docker_runner.run_code()` when enabled
6. Add `docker` package to `pyproject.toml` dependencies

### Phase 2: Feature parity tests

7. Run existing test suite against Docker runner
8. Fix any compatibility issues
9. Run security tests (OOM, fork bomb, infinite loop, network attempt)

### Phase 3: Switch default (next sprint)

10. Change default to Docker
11. Remove subprocess runner
12. Monitor for regressions

### Backward Compatibility

The `run_code(user_code, test_cases) → dict` signature is preserved. The
`exercise.py` router doesn't change — only the import and call.

The language field can be added to the `CodeSubmission` schema as an optional
field (defaults to "python") without breaking existing frontend requests.

## 10. File Layout

```
api/
├── docker/
│   ├── images/
│   │   ├── python/
│   │   │   └── Dockerfile
│   │   ├── node/                     # Future
│   │   │   └── Dockerfile
│   │   └── go/                       # Future
│   │       └── Dockerfile
│   ├── harnesses/
│   │   ├── python_harness.py.j2      # Extracted from current exercise_runner.py
│   │   └── node_harness.js.j2        # Future
│   ├── languages.json                # Language configuration registry
│   └── build_images.sh               # Batch build script
├── app/
│   ├── services/
│   │   ├── docker_runner.py          # NEW — Docker-based runner
│   │   └── exercise_runner.py        # Unchanged (parallel deployment Phase 1)
│   └── config.py                     # Add DOCKER_ENABLED flag
└── pyproject.toml                    # Add `docker` dependency
```

## 11. Comparison Types — Testing Matrix

| Type | Implemented In | Test Exists |
|------|---------------|-------------|
| `exact` | Harness | ✅ `test_exact_*` |
| `regex` | Harness | ✅ `test_regex_*` |
| `non_empty` | Harness | ✅ `test_non_empty_*` |
| `contains` | Harness | ✅ `test_contains_*` |
| `whitelist` | Harness | ✅ `test_whitelist_*` |
| `comment` | Harness | ✅ `test_comment_*` |
| `code_contains` | Harness | ✅ `test_code_contains_*` |
| unknown → exact fallback | Harness | ✅ `test_unknown_type_*` |

All comparison types are tested in the existing test suite. The Docker runner
must pass all of these tests unchanged.

## 12. Open Questions / Decisions Required

1. **Docker SDK vs CLI subprocess?** → SDK preferred for cleaner error handling
2. **Build images on first run vs. separate script?** → Separate build script for MVP;
   auto-build can be added later
3. **Harness location — mounted file vs. embedded in image?** → Mounted file
   (no image rebuild needed for harness changes)
4. **`docker` Python package version?** → Pin to `docker==7.1.0`
5. **Which config format for languages?** → JSON (simple, no extra dependency)

## 13. Security Checklist

- [x] Non-root user inside container
- [x] Read-only root filesystem
- [x] Writable /tmp via tmpfs (noexec, nosuid)
- [x] Network disabled
- [~] Memory cgroup limit (not enforced on RPi — see §4.2)
- [x] CPU cgroup limit
- [x] PIDs cgroup limit
- [x] Seccomp default profile
- [x] All Linux capabilities dropped
- [x] Container timeout with hard kill
- [x] Auto-remove container on exit
- [x] No privileged mode
- [ ] no-new-privileges seccomp rule (hardening)
- [ ] AppArmor profile (hardening)
- [ ] User namespace remapping (hardening)