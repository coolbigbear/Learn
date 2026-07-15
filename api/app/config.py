"""Application configuration."""

import os
from pathlib import Path

# Project root — supports both local dev and Docker layouts.
# In local dev: __file__ = <project>/api/app/config.py  → 3 parents = project root
# In Docker:   __file__ = /app/app/config.py             → 2 parents = /app
# An explicit ROOT_DIR env var overrides both.
ROOT_DIR_ENV = os.environ.get("ROOT_DIR")
if ROOT_DIR_ENV:
    ROOT_DIR = Path(ROOT_DIR_ENV)
else:
    _candidate = Path(__file__).resolve().parent.parent.parent
    if not (_candidate / "api").is_dir():
        _candidate = Path(__file__).resolve().parent.parent
    ROOT_DIR = _candidate

# Database
DATABASE_URL = "sqlite+aiosqlite:///./tutorials.db"

# JWT configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 1 hour default

# Sandbox (subprocess) — limits for the existing subprocess-based runner
MAX_CPU_SECONDS = 2
MAX_MEMORY_MB = 128
MAX_OUTPUT_CHARS = 10_000
WALL_CLOCK_TIMEOUT = 3.0
SHELL_TIMEOUT = 5.0

# Docker sandbox runner configuration
DOCKER_ENABLED = os.environ.get("DOCKER_ENABLED", "true").lower() in ("1", "true", "yes")
DOCKER_TIMEOUT = 5             # Container wall-clock timeout (seconds)
DOCKER_MEMORY_LIMIT = "128m"   # Memory limit per container (Docker format string)
DOCKER_CPU_LIMIT = 500_000_000   # nano_cpus (0.5 CPU)
DOCKER_NETWORK_DISABLED = True
DOCKER_LANGUAGES_CONFIG = ROOT_DIR / "api" / "docker" / "languages.json"
DOCKER_HARNESSES_DIR = ROOT_DIR / "api" / "docker" / "harnesses"

# CORS — origins allowed in development mode
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    # CORS for the ephemeral tunnel domains is handled by PRODUCTION mode
    # (wildcard allow_origins) — see main.py.
]