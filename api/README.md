# Interactive Python Tutorials — Backend API

A FastAPI-based backend for the Interactive Python Tutorials platform. Features user authentication, lesson and exercise management, sandboxed Python code execution, and progress tracking.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) or pip

### Setup

```bash
# 1. Create a virtual environment and install dependencies
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Seed the database with lesson content
python ../scripts/seed_db.py

# 3. Start the dev server
uvicorn app.main:app --reload --port 8000
```

### Verify

```bash
curl http://localhost:8000/api/health
# {"status":"ok"}
```

Open http://localhost:8000/docs for the interactive Swagger UI.

## Environment Variables

All settings have sensible defaults. See `.env.example` for the full list.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./tutorials.db` | Database connection string |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | CORS origins (comma-separated) |

Override any variable by setting it in the environment or in a `.env` file.

## API Endpoints

All endpoints are prefixed with `/api/`. See `/docs` for full OpenAPI docs.

### Auth (`/api/auth`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Create account (username, password) → token |
| POST | `/api/auth/login` | No | Login → token |
| POST | `/api/auth/logout` | Bearer | Invalidate current token |
| GET | `/api/auth/me` | Bearer | Get current user profile |

### Lessons (`/api/lessons`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/lessons` | Bearer | List all lessons with exercise counts |
| GET | `/api/lessons/{slug}` | Bearer | Get lesson detail with exercises (no solutions) |

### Exercises (`/api/exercises`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/exercises/{id}` | Bearer | Get exercise details (starter code, instruction) |
| POST | `/api/exercises/{id}/run` | Bearer | Run code against test cases (no progress saved) |
| POST | `/api/exercises/{id}/submit` | Bearer | Submit code — saves progress if passing |

### Progress (`/api/progress`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/progress` | Bearer | Full progress across all exercises |
| GET | `/api/progress/{lesson_slug}` | Bearer | Progress for a specific lesson |

### Health

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | No | Server health check |

## Authentication

Authentication uses **Bearer tokens**. Register or login to get a token, then include it in requests:

```
Authorization: Bearer <your-token>
```

## Architecture

```
api/
├── app/
│   ├── main.py              # FastAPI app factory, routers, health check
│   ├── config.py            # Configuration constants
│   ├── database.py          # SQLAlchemy async engine + session
│   ├── dependencies.py      # Auth dependency (get_current_user)
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py          # User model (username, hashed password, token)
│   │   ├── lesson.py        # Lesson model (slug, content, order)
│   │   ├── exercise.py      # Exercise model (test_cases stored as JSON)
│   │   └── progress.py      # UserProgress model (per-exercise tracking)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # FastAPI routers (auth, lessons, exercises, progress)
│   └── services/            # Business logic (auth hashing, lesson queries,
│                           #   exercise runner, progress queries)
├── requirements.txt
├── pyproject.toml
└── tests/                   # pytest test suite (38 tests)
    ├── conftest.py          # Async fixtures, test DB, auth headers
    ├── test_auth.py         # Register, login, logout, profile
    ├── test_exercises.py    # Run, submit, get exercise detail
    ├── test_lessons.py      # List lessons, get lesson detail
    └── test_progress.py     # Full progress, per-lesson progress
```

### Exercise Runner

The sandboxed Python execution engine (`app/services/exercise_runner.py`) runs user code in a subprocess with:

- **CPU time limit** (default 2s via `resource.setrlimit`)
- **Memory limit** (default 128 MB via `resource.setrlimit`)
- **Wall-clock timeout** (default 3s via `SIGALRM`)
- **Restricted builtins** (`__import__`, `exec`, `eval`, `compile`, `open` are removed from user code scope)
- **StringIO-based I/O capture** (stdin/stdout/stderr are captured per test case)

## Testing

```bash
cd api
source .venv/bin/activate
pytest -v
```

All 38 tests should pass. Tests use an in-memory SQLite database and are fully isolated.

## Content

Lesson content lives in `content/` at the project root. Each lesson is a directory with:

- `lesson.md` — Lesson text in Markdown
- `exercises.json` — Array of exercise objects with test cases

Run the seed script to load it into the database:

```bash
python scripts/seed_db.py
```

<!-- CI test PR #12 verification - dummy change -->
