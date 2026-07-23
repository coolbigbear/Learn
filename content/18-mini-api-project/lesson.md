# Lesson 23: Mini API Project

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Build a complete CRUD API from scratch
> - Create an in-memory data store
> - Handle all four HTTP methods: GET, POST, PUT, DELETE
> - Use path and query parameters together
> - Return proper HTTP status codes

---

## Project Overview

In this lesson, you'll build a **Task Manager API** — a simple service that lets users create, read, update, and delete tasks. You'll use an in-memory list to store the tasks.

This is your capstone project. By the end, you'll have built a real, working API that follows RESTful conventions.

---

## Setup

Start with a fresh FastAPI app in `main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task Manager API")

# In-memory database
tasks = []
next_id = 1
```

---

## Models

Define a Pydantic model for tasks:

```python
class Task(BaseModel):
    title: str
    completed: bool = False

class TaskResponse(Task):
    id: int
```

We'll use `Task` for creating tasks and `TaskResponse` for returning them.

---

## Create a Task (POST)

```python
@app.post("/tasks", status_code=201)
async def create_task(task: Task):
    global next_id
    new_task = {"id": next_id, **task.model_dump()}
    tasks.append(new_task)
    next_id += 1
    return new_task
```

---

## List All Tasks (GET)

```python
@app.get("/tasks")
async def list_tasks(completed: bool | None = None):
    if completed is None:
        return tasks
    return [t for t in tasks if t["completed"] == completed]
```

The optional `completed` query parameter lets you filter by status.

---

## Get a Single Task (GET)

```python
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")
```

---

## Update a Task (PUT)

```python
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, updated: Task):
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = updated.title
            task["completed"] = updated.completed
            return task
    raise HTTPException(status_code=404, detail="Task not found")
```

---

## Delete a Task (DELETE)

```python
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail="Task not found")
```

Returning `204 No Content` indicates successful deletion with no response body.

---

## Run and Test

Start your server with `uvicorn main:app --reload`, then:

- **Create a task:** `POST /tasks` with `{"title": "Learn FastAPI"}`
- **List tasks:** `GET /tasks`
- **Get task 1:** `GET /tasks/1`
- **Update task 1:** `PUT /tasks/1` with `{"title": "Master FastAPI", "completed": true}`
- **Delete task 1:** `DELETE /tasks/1`

Visit `/docs` to test everything interactively!

---

## Common Mistakes

- **Forgetting to import `HTTPException`** — It's `from fastapi import HTTPException`, not from anywhere else. Without it, you can't return proper error status codes.
- **Using mutable default values** — Don't use `[]` or `{}` as function defaults. They're shared across calls. Use `None` and handle it inside the function.
- **Not raising `HTTPException` on missing resources** — When a task isn't found, return `404` with `HTTPException`, not a 200 with an error message.
- **Hardcoding `status_code=200` for everything** — POST should return `201`, DELETE should return `204`. Use the right status code for the operation.
- **Forgetting to restart the server** — FastAPI with `--reload` handles this, but if you're not using `--reload`, restart `uvicorn` after every code change.

## Best Practices

1. **Use Pydantic models for both request and response** — Define separate models for input (`Task`) and output (`TaskResponse`) so you control what the client sees.
2. **Return meaningful HTTP status codes** — `201` for creation, `204` for deletion, `404` for not found, `422` for validation errors.
3. **Use path parameters for resource identifiers** — `/tasks/{task_id}` is RESTful; `/tasks?task_id=1` is not.
4. **Filter with query parameters** — The `completed` filter in the list endpoint is a clean pattern for optional filtering.
5. **Test all CRUD operations** — Use `/docs` or `curl` to test create, read, update, and delete — including error cases like requesting a non-existent task.

---

## Summary

- You built a complete CRUD API with FastAPI
- In-memory storage is fine for learning; real apps use databases
- HTTP status codes communicate success or failure clearly
- RESTful conventions make your API predictable and easy to use
