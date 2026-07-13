# Interactive Python Tutorials — Architecture Specification

## 1. System Overview

A web application that teaches Python programming through interactive,
browser-based tutorials. Students write and run Python code in-browser,
progressing from "Hello World" through building their own FastAPI API.

```
┌─────────────────────┐      ┌─────────────────────┐
│                     │      │                     │
│   React SPA         │◄────►│   FastAPI Server    │
│   (CodeMirror 6)    │ REST │                     │
│   (React Router)    │      │   SQLite (via       │
│   (rehype + remark) │      │   SQLAlchemy +      │
│                     │      │   aiosqlite)        │
└─────────────────────┘      │                     │
                             │   Sandboxed Python  │
                             │   Runner (subprocess│
                             │   + resource limits)│
                             └─────────────────────┘
```

## 2. Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Backend framework | FastAPI (Python 3.13) | Async, auto-docs, modern Python |
| Database | SQLite via SQLAlchemy async | Zero-setup, single file, good enough for a tutorial app |
| Auth | Token-based (on User model) | Simple, no OAuth complexity |
| Code execution | `subprocess` with resource limits | Lightweight sandbox, no Docker needed for a teaching tool |
| Frontend framework | React 18 (Vite) | Fast dev, broad ecosystem |
| Code editor | CodeMirror 6 | Lighter than Monaco, good Python syntax support |
| Markdown rendering | react-markdown + rehype/remark | Extensible pipeline for code blocks & exercise widgets |
| Routing | React Router v6 | SPA routing |
| Styling | Tailwind CSS 3 | Utility-first, fast iteration |
| Testing (backend) | pytest + httpx (AsyncClient) | Standard FastAPI testing |
| Testing (frontend) | Vitest + React Testing Library | Fast, Vite-native |
| E2E | Playwright | Industry standard |

## 3. Directory Layout

```
/opt/data/projects/python-tutorials/
├── api/                          # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app factory
│   │   ├── config.py             # Settings / env
│   │   ├── database.py           # SQLAlchemy async engine + sessions
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── lesson.py
│   │   │   ├── exercise.py
│   │   │   └── progress.py
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── lesson.py
│   │   │   ├── exercise.py
│   │   │   └── progress.py
│   │   ├── routers/              # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── lessons.py
│   │   │   ├── exercises.py
│   │   │   └── progress.py
│   │   ├── services/             # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── lesson.py
│   │   │   ├── exercise_runner.py  # Sandboxed Python execution
│   │   │   └── progress.py
│   │   └── dependencies.py       # FastAPI dependencies (get_db, get_current_user)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_lessons.py
│   │   ├── test_exercises.py
│   │   └── test_progress.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── alembic/ (optional — use auto-create tables for MVP)
│
├── frontend/                     # React SPA
│   ├── src/
│   │   ├── main.jsx              # Entry point
│   │   ├── App.jsx               # Router + layout
│   │   ├── api/                  # Axios/fetch client
│   │   │   └── client.js
│   │   ├── components/           # Reusable UI components
│   │   │   ├── Layout.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── LessonCard.jsx
│   │   │   ├── CodeEditor.jsx    # CodeMirror wrapper
│   │   │   ├── OutputPanel.jsx
│   │   │   ├── ExerciseFeedback.jsx
│   │   │   └── ProgressBar.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Lessons.jsx       # Lesson list
│   │   │   ├── LessonView.jsx    # Single lesson + exercises
│   │   │   └── Progress.jsx
│   │   ├── hooks/                # Custom hooks
│   │   │   ├── useAuth.js
│   │   │   └── useProgress.js
│   │   └── styles/               # Tailwind + custom CSS
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── tests/
│       ├── setup.js
│       └── ...
│
├── content/                      # Tutorial lessons
│   ├── 01-hello-world/
│   │   ├── lesson.md
│   │   └── exercises.json
│   ├── 02-variables/
│   │   ├── lesson.md
│   │   └── exercises.json
│   ├── 03-strings/
│   │   ├── lesson.md
│   │   └── exercises.json
│   ├── ... (through 15-lessons)
│   └── manifest.json             # Ordered list of all lessons
│
├── docs/
│   ├── ARCHITECTURE.md           # This file
│   └── API.md                    # API Specification
│
├── scripts/                      # Utility scripts
│   ├── seed_db.py                # Populate lessons into DB
│   └── run.sh                    # Dev startup
│
├── brief.md
├── TEAM.md
└── pyproject.toml                # Root project metadata
```

## 4. Data Model

### 4.1 Entities

**User**
- id: int (PK, auto)
- username: str (unique)
- password_hash: str
- token: str (unique, nullable — generated on login)
- created_at: datetime

**Lesson**
- id: int (PK, auto)
- slug: str (unique — e.g. "01-hello-world")
- title: str
- content: str (markdown body)
- order: int
- created_at: datetime

**Exercise**
- id: int (PK, auto)
- lesson_id: int (FK → Lesson.id)
- slug: str (unique — e.g. "hello-print")
- title: str
- instruction: str (markdown)
- starter_code: str (text)
- solution_code: str (text)
- test_cases: JSON (list of {input, expected_output, comparison_type})
- order: int

**UserProgress**
- id: int (PK, auto)
- user_id: int (FK → User.id)
- exercise_id: int (FK → Exercise.id)
- completed: bool
- code_submitted: str (text)
- attempts: int
- completed_at: datetime (nullable)
- UNIQUE(user_id, exercise_id)

### 4.2 ER Diagram (text)

```
User 1──* UserProgress *──1 Exercise *──1 Lesson
```

## 5. Code Execution Sandbox

Python user code runs via `subprocess` with strict resource limits:

- CPU time: max 2 seconds (via `resource.setrlimit`)
- Memory: max 128 MB (via `resource.setrlimit`)
- Filesystem: temporary directory, cleaned after execution
- Disabled builtins: `__import__`, `open`, `exec`, `eval`, `compile`
- Whitelisted modules: none by default — only stdlib
- Output capture: stdout + stderr (last 10KB each)
- Timeout: SIGALRM after 3 seconds wall clock

The runner wraps user code in a harness that:
1. Injects test input via stdin
2. Captures stdout/stderr
3. Compares output to expected using exact string match or regex
4. Returns {passed: bool, actual_output: str, expected_output: str, errors: str}

For safety, each execution forks into a child process so the parent is never corrupted.

## 6. Auth Flow

1. POST /api/auth/register — creates user, returns token
2. POST /api/auth/login — validates credentials, returns token
3. All other endpoints require `Authorization: Bearer <token>` header
4. Token is a UUID stored on the User model — simple, no JWT complexity
5. Token checked via FastAPI dependency `get_current_user`

## 7. Error Handling

All API errors return:

```json
{
  "detail": "Human-readable error message"
}
```

Standard HTTP codes: 200, 201, 400, 401, 404, 409, 422, 500.

## 8. CORS

During development, FastAPI CORS middleware allows `http://localhost:5173` (Vite dev server). In production, restrict to the deployed frontend domain.