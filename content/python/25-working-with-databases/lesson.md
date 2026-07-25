# Lesson 25: Working with Databases

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand why databases are essential for real-world applications
> - Use SQLite — the built-in Python database — with the `sqlite3` module
> - Model data with SQLAlchemy ORM tables and relationships
> - Perform CRUD operations (Create, Read, Update, Delete) with async sessions
> - Manage database connections with connection pooling
> - Handle database errors with transactions and rollbacks
> - Connect a FastAPI application to a database using the async session pattern
> - Convert an in-memory API to use persistent SQLite storage

---

## Why Databases?

Think about the Task Manager API you built in Lesson 24. It worked, but it had a big problem: **every time you restarted the server, all your tasks disappeared!**

The data lived in a Python list inside the process memory. When the process stopped, the memory was reclaimed and your data was gone.

**Databases solve this by providing:**
- **Persistence** — data survives restarts and power failures
- **Concurrency** — multiple users can read/write at the same time
- **Querying** — find, filter, and sort data efficiently
- **Integrity** — rules that keep your data consistent (e.g., no duplicate usernames)

In this lesson, you'll learn how to connect your APIs to a real database so data lives forever.

---

## SQLite — The Built-in Database

SQLite is the most widely deployed database in the world. It's in your phone, your browser, and even some airplanes!

**What makes SQLite special:**
- **No separate server** — the database is just a file
- **Zero configuration** — `import sqlite3` and you're ready
- **Built into Python** — no extra packages to install
- **Perfect for learning** — same SQL concepts apply to PostgreSQL, MySQL, etc.

### Raw SQLite with Python

Let's start with Python's built-in `sqlite3` module to understand the basics:

```python
import sqlite3

# Connect to a database file (creates it if it doesn't exist)
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

# Create a table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        completed INTEGER DEFAULT 0
    )
""")

# Insert a row
cursor.execute(
    "INSERT INTO tasks (title) VALUES (?)",
    ("Learn SQLite",)
)
conn.commit()  # <-- Save changes

# Query rows
cursor.execute("SELECT * FROM tasks")
print(cursor.fetchall())  # [(1, 'Learn SQLite', 0)]

# Close when done
conn.close()
```

> **Note:** Use `?` placeholders instead of f-strings to prevent **SQL injection attacks** — never interpolate user input directly into SQL strings!

This works, but writing raw SQL strings in Python gets tedious and error-prone. For our APIs, we'll use a higher-level tool: **SQLAlchemy**.

---

## Introducing SQLAlchemy

SQLAlchemy is the most popular Python database toolkit. It provides an **ORM** (Object-Relational Mapper) that lets you work with database tables using Python classes and objects instead of writing SQL strings.

The platform you're learning on already has SQLAlchemy installed. Here's the core idea:

```python
# Instead of writing:
cursor.execute("INSERT INTO users (name) VALUES ('Alice')")

# You write:
db.add(User(name="Alice"))
await db.commit()
```

### Core Concepts

SQLAlchemy has three main pieces:

| Concept | What it does |
|---------|-------------|
| **Engine** | Manages the connection pool to the database |
| **Session** | A workspace where you interact with the database |
| **Model** | A Python class that represents a database table |

### Async Setup for FastAPI

Since FastAPI is async, we use SQLAlchemy's async support with `aiosqlite`:

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase

# 1. Create the engine (connects to the database file)
engine = create_async_engine(
    "sqlite+aiosqlite:///./tasks.db",
    connect_args={"check_same_thread": False},
    echo=False,
)

# 2. Create a session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3. Define a base class for models
class Base(DeclarativeBase):
    pass
```

This is exactly the pattern used in the platform's own database setup!

---

## Defining Models

A **model** is a Python class that maps to a database table. Each attribute becomes a column.

```python
from sqlalchemy import Column, Integer, String, Boolean

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)
```

When you define a model, SQLAlchemy can create the actual table in the database:

```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

> `create_all` is safe to call on every startup — it uses `IF NOT EXISTS` internally.

### Common Column Types

| SQLAlchemy Type | Python Type | SQLite Type |
|----------------|-------------|-------------|
| `Integer` | `int` | INTEGER |
| `String(N)` | `str` (max N chars) | TEXT |
| `Boolean` | `bool` | INTEGER (0/1) |
| `Float` | `float` | REAL |
| `DateTime` | `datetime` | TEXT (ISO format) |
| `Text` | `str` (unlimited) | TEXT |

### Column Options

```python
Column(Integer, primary_key=True)          # Primary key
Column(String, unique=True)                # No duplicates allowed
Column(String, nullable=False)             # Required field
Column(Integer, default=0)                 # Default value
Column(String, index=True)                 # Faster lookups
```

---

## CRUD Operations with Async Sessions

Now the fun part — actually using the database! Let's look at each CRUD operation.

### Create

```python
async def create_task(title: str) -> Task:
    async with async_session_factory() as session:
        task = Task(title=title)
        session.add(task)
        await session.commit()
        await session.refresh(task)  # Load the auto-generated id
        return task
```

### Read (Get by ID)

```python
async def get_task(task_id: int) -> Task | None:
    async with async_session_factory() as session:
        return await session.get(Task, task_id)
```

### Read (Query with Filters)

```python
from sqlalchemy import select

async def list_tasks(completed: bool | None = None) -> list[Task]:
    async with async_session_factory() as session:
        stmt = select(Task)
        if completed is not None:
            stmt = stmt.where(Task.completed == completed)
        result = await session.execute(stmt)
        return result.scalars().all()
```

### Update

```python
async def update_task(task_id: int, title: str) -> Task | None:
    async with async_session_factory() as session:
        task = await session.get(Task, task_id)
        if task is None:
            return None
        task.title = title
        await session.commit()
        return task
```

### Delete

```python
async def delete_task(task_id: int) -> bool:
    async with async_session_factory() as session:
        task = await session.get(Task, task_id)
        if task is None:
            return False
        await session.delete(task)
        await session.commit()
        return True
```

> `session.refresh()` reloads the object from the database — use it after `commit()` to get server-generated values like auto-increment IDs.

---

## Connection Pooling and Session Management

### What is Connection Pooling?

Opening a database connection is slow. **Connection pooling** keeps a pool of ready-to-use connections so your app doesn't have to open a new one for every request.

SQLAlchemy's `create_async_engine` creates a connection pool automatically. You can configure it:

```python
engine = create_async_engine(
    "sqlite+aiosqlite:///./tasks.db",
    pool_size=5,        # Keep 5 connections ready
    max_overflow=10,    # Allow up to 10 extra during spikes
    pool_pre_ping=True, # Test connections before using them
)
```

### The Session Pattern for FastAPI

In a FastAPI app, you don't want to create a session inside every endpoint. Instead, use a **dependency** that provides a session to each request:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

async def get_db() -> AsyncSession:
    """FastAPI dependency: yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

@app.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)):
    stmt = select(Task)
    result = await db.execute(stmt)
    return result.scalars().all()

@app.post("/tasks")
async def create_task(title: str, db: AsyncSession = Depends(get_db)):
    task = Task(title=title)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
```

This pattern is used by the platform itself! The dependency:
1. Creates a new session for each request
2. Commits on success
3. Rolls back on error (preventing partial saves)

> **Key Insight:** The `connection pool` is shared across requests (managed by the engine), but each request gets its own `session` — a clean workspace.

---

## Error Handling

Database operations can fail. Here's how to handle the most common issues:

### Integrity Errors

```python
from sqlalchemy.exc import IntegrityError

async def create_user(username: str):
    async with async_session_factory() as session:
        try:
            user = User(username=username)
            session.add(user)
            await session.commit()
            return user
        except IntegrityError:
            await session.rollback()
            raise ValueError(f"Username '{username}' already exists")
```

### Transaction Rollback

A **transaction** is a unit of work. If any part fails, the whole transaction is rolled back:

```python
async def transfer_money(sender_id: int, receiver_id: int, amount: float):
    async with async_session_factory() as session:
        try:
            sender = await session.get(Account, sender_id)
            receiver = await session.get(Account, receiver_id)

            sender.balance -= amount
            receiver.balance += amount

            await session.commit()  # Both updates happen together, or neither
        except Exception:
            await session.rollback()
            raise
```

### Connection Errors

```python
from sqlalchemy.exc import OperationalError

async def safe_query():
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(Task))
            return result.scalars().all()
    except OperationalError as e:
        print(f"Database unavailable: {e}")
        return []  # Graceful degradation
```

---

## End-to-End: Task Manager with SQLite

Let's bring everything together by converting the Lesson 24 Task Manager to use a real SQLite database.

Create `main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# ── Database Setup ──────────────────────────────────────────────────────────

engine = create_async_engine(
    "sqlite+aiosqlite:///./tasks.db",
    connect_args={"check_same_thread": False},
)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)


# ── App Setup ───────────────────────────────────────────────────────────────

app = FastAPI(title="Task Manager DB")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── Pydantic Schemas ────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = {"from_attributes": True}


# ── Dependency ──────────────────────────────────────────────────────────────

async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.post("/tasks", status_code=201)
async def create_task(body: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = TaskDB(title=body.title)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@app.get("/tasks")
async def list_tasks(
    completed: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TaskDB)
    if completed is not None:
        stmt = stmt.where(TaskDB.completed == completed)
    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(TaskDB, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    body: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(TaskDB, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if body.title is not None:
        task.title = body.title
    if body.completed is not None:
        task.completed = body.completed
    await db.commit()
    return task


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(TaskDB, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
```

### What Changed from the In-Memory Version?

| Before (Lesson 24) | After (Lesson 25) |
|--------------------|--------------------|
| `tasks = []` — a Python list | `TaskDB` — a SQLAlchemy model |
| `next_id` counter | Auto-incrementing `id` column |
| Manual list operations | `session.add()`, `session.get()`, `session.delete()` |
| No commit needed | `await session.commit()` |

### Running It

Start the server:

```bash
uvicorn main:app --reload
```

Test it the same way as before — visit `/docs` or use curl. But now your tasks survive a server restart! Try it: create a task, stop the server (Ctrl+C), start it again, and list tasks.

> **Pro tip:** `--reload` is great for development, but in production you'd omit it. The database file `tasks.db` will appear in your project directory after the first request.

---

## Common Mistakes

- **Forgetting to await DB queries** — SQLAlchemy async queries need `await session.execute(...)`. Without `await`, you get a coroutine object, not the result.
- **Not closing database sessions** — Always use `async with` or a dependency generator to ensure sessions are closed. Leaked sessions exhaust the connection pool.
- **Hardcoding connection strings** — `DATABASE_URL` should come from an environment variable, not be hardcoded. Different environments (dev, test, prod) need different databases.
- **Mixing sync and async SQLAlchemy** — Don't use `from sqlalchemy import create_engine` with async endpoints. Use `create_async_engine` for async code.
- **Catching exceptions too broadly** — Catching all exceptions in DB code can hide real errors. Catch specific exceptions like `IntegrityError` and let unexpected ones propagate.

## Best Practices

1. **Use the `get_db` dependency pattern** — A generator function that yields a session and handles commit/rollback in `finally` is the standard FastAPI approach.
2. **Always use async SQLAlchemy with FastAPI** — Async sessions don't block the event loop. Sync sessions can, under load, slow down all concurrent requests.
3. **Define models with explicit column types** — `Column(Integer)`, `Column(String(100))`, not just `Column()`. Explicit types improve readability and portability.
4. **Use environment variables for `DATABASE_URL`** — Keep connection strings out of source code. Use `os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tasks.db")` for a sensible default.
5. **Add indexes for frequently queried columns** — Foreign keys and columns used in `WHERE` clauses should have indexes for performance.

---

## Summary

- **Databases** provide persistence, concurrency, and data integrity
- **SQLite** is a zero-configuration, serverless database built into Python
- **SQLAlchemy ORM** lets you work with database tables as Python classes
- **Models** define your table structure with columns and types
- **Async sessions** integrate naturally with FastAPI — one session per request
- **Connection pooling** reuses database connections efficiently
- **Transactions** ensure that operations either fully succeed or fully fail
- The `get_db` **dependency pattern** handles commit/rollback automatically

### What's Next

Now that you can connect your API to a database, you're ready to add **user authentication** — protecting your endpoints so only authenticated users can create, update, or delete data.
