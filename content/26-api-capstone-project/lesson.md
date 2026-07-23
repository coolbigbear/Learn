# Lesson 26: API Capstone Project — Full-Stack Task Manager

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Structure a real-world FastAPI project across multiple modules
> - Connect FastAPI to a SQLite database using SQLAlchemy ORM
> - Implement user registration and login with JWT authentication
> - Build protected CRUD endpoints with ownership checks
> - Hash passwords securely and validate user input
> - Apply professional error handling and status codes
> - Use dependency injection for clean, reusable authentication

---

## Project Overview

So far you've learned to build APIs with FastAPI, handle JSON payloads, understand HTTP status codes, make HTTP requests, and manage authentication. Now it's time to bring everything together into a **complete, database-backed, authenticated API**.

We'll build a **Task Manager API** with these features:

| Feature | Description |
|---------|-------------|
| User Registration | Sign up with username and password |
| User Login | Authenticate and receive a JWT token |
| Task CRUD | Create, read, update, and delete tasks |
| Task Ownership | Each user sees and manages only their own tasks |
| Persistence | All data stored in a SQLite database |
| Security | Passwords hashed with bcrypt, endpoints protected with JWT |

This is the project structure we'll build:

```
project/
├── main.py          # FastAPI app and route wiring
├── database.py      # SQLAlchemy engine and session
├── models.py        # ORM models (User, Task)
├── schemas.py       # Pydantic request/response schemas
└── auth.py          # Password hashing, JWT, get_current_user
```

---

## 1. Project Setup and Dependencies

First, install the required packages:

```bash
pip install fastapi uvicorn sqlalchemy aiosqlite passlib[bcrypt] python-jose[cryptography]
```

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `sqlalchemy` | ORM for database operations |
| `aiosqlite` | Async SQLite driver |
| `passlib[bcrypt]` | Password hashing |
| `python-jose` | JWT token creation and verification |

---

## 2. Database Configuration (`database.py`)

We'll use SQLAlchemy's **async** API with SQLite. This keeps things simple for development while teaching a pattern that works with PostgreSQL in production.

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./tasks.db"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency that provides a database session."""
    async with async_session() as session:
        yield session
```

Key points:
- `create_async_engine` sets up the connection pool
- `async_sessionmaker` creates new session objects
- `Base` is the declarative base all models inherit from
- `init_db()` creates tables on startup
- `get_db()` is a FastAPI dependency that provides a session per request

---

## 3. ORM Models (`models.py`)

We need two models: `User` for authentication and `Task` for the todo items.

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)

    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="tasks")
```

**Relationships are powerful:**
- `User.tasks` gives you all tasks belonging to a user
- `Task.owner` gives you the user who owns a task
- `cascade="all, delete-orphan"` means deleting a user deletes their tasks too
- `ForeignKey("users.id")` ensures referential integrity at the database level

---

## 4. Pydantic Schemas (`schemas.py`)

Pydantic models handle request validation and define the API contract:

```python
from pydantic import BaseModel
from typing import Optional


# ── Auth Schemas ──

class SignupRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Task Schemas ──

class TaskCreate(BaseModel):
    title: str
    completed: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    owner_id: int

    model_config = {"from_attributes": True}
```

Using `from_attributes = True` (Pydantic v2) lets us return ORM objects directly — FastAPI will convert them to the response schema automatically.

---

## 5. Authentication Module (`auth.py`)

This is the heart of our security. It handles password hashing, JWT creation, and the `get_current_user` dependency.

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User

# ── Configuration ──
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ── Password Hashing ──
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ── JWT Tokens ──
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# ── Auth Dependency ──
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT token."""
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

**How it works:**

1. `hash_password()` uses bcrypt to create a one-way hash — never store raw passwords
2. `verify_password()` checks a plain-text password against a stored hash
3. `create_access_token()` generates a JWT with an expiration time
4. `decode_token()` validates and decodes a JWT, returning `None` if invalid
5. `get_current_user()` is a **dependency** that extracts the Bearer token, decodes it, looks up the user, and returns them. You can inject this into any protected endpoint.

---

## 6. Main Application (`main.py`)

Finally, we wire everything together. This is where all the routes are defined.

```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import init_db, get_db
from models import User, Task
from schemas import (
    SignupRequest, LoginRequest, TokenResponse,
    TaskCreate, TaskUpdate, TaskResponse
)
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user
)

app = FastAPI(title="Task Manager API")


@app.on_event("startup")
async def startup():
    await init_db()


# ── Auth Endpoints ──

@app.post("/auth/signup", status_code=201)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    result = await db.execute(
        select(User).where(User.username == body.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username}


@app.post("/auth/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive a JWT token."""
    result = await db.execute(
        select(User).where(User.username == body.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


# ── Task Endpoints (Protected) ──

@app.get("/tasks")
async def list_tasks(
    completed: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List tasks for the current user, optionally filtered by status."""
    query = select(Task).where(Task.owner_id == current_user.id)
    if completed is not None:
        query = query.where(Task.completed == completed)
    query = query.order_by(Task.id)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@app.post("/tasks", status_code=201)
async def create_task(
    body: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task owned by the current user."""
    task = Task(
        title=body.title,
        completed=body.completed,
        owner_id=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@app.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single task (must own it)."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    body: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a task's title and/or completed status."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if body.title is not None:
        task.title = body.title
    if body.completed is not None:
        task.completed = body.completed

    await db.commit()
    await db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task (must own it)."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
```

---

## 7. How to Run and Test

Start the server:

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

**Test the full workflow:**

```python
import requests

BASE = "http://localhost:8000"

# 1. Sign up
r = requests.post(f"{BASE}/auth/signup", json={
    "username": "alice", "password": "secret123"
})
print("Signup:", r.status_code, r.json())

# 2. Login
r = requests.post(f"{BASE}/auth/login", json={
    "username": "alice", "password": "secret123"
})
token = r.json()["access_token"]
print("Token:", token[:20] + "...")

headers = {"Authorization": f"Bearer {token}"}

# 3. Create tasks
r = requests.post(f"{BASE}/tasks", json={
    "title": "Learn FastAPI", "completed": False
}, headers=headers)
print("Created:", r.json())

r = requests.post(f"{BASE}/tasks", json={
    "title": "Build a capstone project", "completed": False
}, headers=headers)
print("Created:", r.json())

# 4. List tasks
r = requests.get(f"{BASE}/tasks", headers=headers)
print("Tasks:", r.json())

# 5. Update a task
r = requests.put(f"{BASE}/tasks/1", json={"completed": True}, headers=headers)
print("Updated:", r.json())

# 6. Delete a task
r = requests.delete(f"{BASE}/tasks/2", headers=headers)
print("Deleted:", r.status_code)
```

---

## 8. Key Design Decisions

### Why async?

Async SQLAlchemy with `aiosqlite` lets FastAPI handle many requests concurrently. In a real deployment with PostgreSQL, this gives you excellent throughput without complex threading.

### Why dependency injection for auth?

The `get_current_user` dependency encapsulates all authentication logic. Adding `current_user: User = Depends(get_current_user)` to any endpoint instantly protects it. To change the auth mechanism, you change one function — not every endpoint.

### Why ownership checks?

Every task query includes `Task.owner_id == current_user.id`. This ensures users can only access their own data — a fundamental security principle called **tenant isolation** or **multi-tenancy**.

### Status codes used:

| Code | When |
|------|------|
| **200** | Successful GET, PUT |
| **201** | Created via POST (signup, create task) |
| **204** | Successful DELETE (no body) |
| **400** | Bad request (username already exists) |
| **401** | Unauthorized (invalid token, bad credentials) |
| **404** | Not found (task doesn't exist or doesn't belong to user) |

---

## 9. Summary

In this capstone project, you built a complete, production-style API:

- **Multiple files** — organized by concern (models, schemas, auth, database, routes)
- **Database persistence** — SQLite with async SQLAlchemy ORM
- **User authentication** — bcrypt password hashing and JWT tokens
- **Protected endpoints** — dependency injection for clean auth
- **Ownership isolation** — users only see their own data
- **Proper status codes** — 201 for creation, 204 for deletion, 401 for auth failures
- **Error handling** — clear error messages and appropriate HTTP codes

This architecture scales to real applications. The same patterns — async database, JWT auth, dependency injection, ownership checks — are used by production FastAPI services handling millions of requests.

---

## Common Mistakes

- **Not hashing passwords** — Store password hashes (with bcrypt or similar), never plain text. A database breach would expose every user's password.
- **Skipping input validation** — Always validate request data with Pydantic models. Missing validators can lead to SQL injection, broken queries, or data corruption.
- **Exposing internal error details** — Don't return Python tracebacks or SQLAlchemy errors to the client. Use custom exception handlers for clean, safe error responses.
- **Forgetting ownership checks** — A user should only see and modify their own tasks. Without ownership checks in every endpoint, users can access each other's data.
- **Not handling database connection errors** — If the database is down, your API should return a 503 error, not crash with an unhandled exception.

## Best Practices

1. **Use dependency injection for auth and DB** — The `get_current_user` and `get_db` patterns keep your endpoints clean and testable.
2. **Hash passwords with bcrypt** — Use `passlib` with the `bcrypt` scheme. It's the industry standard for password hashing.
3. **Separate concerns into modules** — Keep `database.py`, `models.py`, `schemas.py`, and `auth.py` separate. It scales much better than one giant `main.py`.
4. **Use environment variables for configuration** — Database URLs, secret keys, and API endpoints should all come from `os.getenv()`.
5. **Test every endpoint** — Write tests for success cases (200, 201, 204) and error cases (401, 403, 404) for every endpoint in your API.

---

## Summary

- You built a complete, production-style Task Manager API with user registration, JWT authentication, and database-backed CRUD
- **SQLAlchemy** with async SQLite provides persistent storage that survives server restarts
- **JWT tokens** enable stateless authentication — the server verifies the token without a database lookup
- **Password hashing** with bcrypt ensures user credentials stay secure even if the database is compromised
- **Ownership checks** isolate each user's data — users can only see and modify their own tasks
- The project structure (`main.py`, `database.py`, `models.py`, `schemas.py`, `auth.py`) scales to real-world applications

### What's Next?

You've completed the API section! These skills transfer directly to:
- Building RESTful microservices
- Creating authentication systems
- Designing database-backed applications
- Writing clean, maintainable Python APIs

Consider exploring:
- **PostgreSQL** instead of SQLite for production
- **Role-based access control** (admin vs regular users)
- **Pagination** for large task lists
- **Unit tests** with pytest and httpx
