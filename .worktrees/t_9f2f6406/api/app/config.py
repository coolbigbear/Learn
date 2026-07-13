"""Application configuration."""

from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Database
DATABASE_URL = "sqlite+aiosqlite:///./tutorials.db"

# Auth token length
TOKEN_BYTES = 24  # 48 hex chars

# Sandbox
MAX_CPU_SECONDS = 2
MAX_MEMORY_MB = 128
MAX_OUTPUT_CHARS = 10_000
WALL_CLOCK_TIMEOUT = 3.0
SHELL_TIMEOUT = 5.0

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
