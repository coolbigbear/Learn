# Interactive Python Tutorials — API Specification

Base URL: `http://localhost:8000/api`

All endpoints (except auth) require `Authorization: Bearer <token>` header.

---

## Auth

### POST /api/auth/register

Create a new user account.

**Request body:**
```json
{
  "username": "alice",
  "password": "supersecret123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "alice",
  "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Errors:** 409 (username taken), 422 (validation)

### POST /api/auth/login

Authenticate and receive a token.

**Request body:**
```json
{
  "username": "alice",
  "password": "supersecret123"
}
```

**Response (200):**
```json
{
  "id": 1,
  "username": "alice",
  "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Errors:** 401 (bad credentials), 422 (validation)

### POST /api/auth/logout

Invalidate the current token.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "detail": "Logged out"
}
```

---

## Lessons

### GET /api/lessons

List all lessons (ordered).

**Response (200):**
```json
{
  "lessons": [
    {
      "id": 1,
      "slug": "01-hello-world",
      "title": "Hello, World!",
      "order": 1,
      "exercise_count": 3
    }
  ]
}
```

### GET /api/lessons/{slug}

Get a single lesson with its exercises.

**Response (200):**
```json
{
  "id": 1,
  "slug": "01-hello-world",
  "title": "Hello, World!",
  "content": "# Hello, World!\n\nIn Python, you print with...",
  "order": 1,
  "exercises": [
    {
      "id": 1,
      "slug": "hello-print",
      "title": "Print your name",
      "instruction": "Write code to print your name.",
      "starter_code": "# Write your code here\n",
      "order": 1
    }
  ]
}
```

Note: `solution_code` and `test_cases` are NEVER returned to the client.

---

## Exercises

### POST /api/exercises/{exercise_id}/run

Submit code for execution against test cases.

**Headers:** `Authorization: Bearer <token>`

**Request body:**
```json
{
  "code": "print('hello')"
}
```

**Response (200):**
```json
{
  "passed": true,
  "actual_output": "hello\n",
  "expected_output": "hello\n",
  "errors": null,
  "test_results": [
    {
      "test_index": 0,
      "passed": true,
      "actual_output": "hello\n",
      "expected_output": "hello\n",
      "errors": null
    }
  ]
}
```

**Response (200, failed):**
```json
{
  "passed": false,
  "actual_output": "HELLO\n",
  "expected_output": "hello\n",
  "errors": null,
  "test_results": [
    {
      "test_index": 0,
      "passed": false,
      "actual_output": "HELLO\n",
      "expected_output": "hello\n",
      "errors": null
    }
  ]
}
```

**Response (200, error):**
```json
{
  "passed": false,
  "actual_output": "",
  "expected_output": "hello\n",
  "errors": "NameError: name 'pront' is not defined\n",
  "test_results": [
    {
      "test_index": 0,
      "passed": false,
      "actual_output": "",
      "expected_output": "hello\n",
      "errors": "NameError: name 'pront' is not defined\n"
    }
  ]
}
```

**Errors:** 401 (unauthorized), 404 (exercise not found)

### POST /api/exercises/{exercise_id}/submit

Submit exercise as completed (marks progress and runs tests).

**Headers:** `Authorization: Bearer <token>`

**Request body:**
```json
{
  "code": "print('hello')"
}
```

**Response (200):**
```json
{
  "passed": true,
  "actual_output": "hello\n",
  "expected_output": "hello\n",
  "errors": null,
  "test_results": [
    {
      "test_index": 0,
      "passed": true,
      "actual_output": "hello\n",
      "expected_output": "hello\n",
      "errors": null
    }
  ]
}
```

If `passed == true`, the exercise is marked as completed in `UserProgress`.

---

## Progress

### GET /api/progress

Get the authenticated user's progress across all exercises.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "progress": [
    {
      "exercise_id": 1,
      "exercise_slug": "hello-print",
      "lesson_slug": "01-hello-world",
      "completed": true,
      "attempts": 3,
      "completed_at": "2026-07-01T12:00:00Z"
    }
  ],
  "summary": {
    "total_exercises": 45,
    "completed_exercises": 12,
    "percentage": 26.7
  }
}
```

### GET /api/progress/{lesson_slug}

Get progress for a specific lesson's exercises.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "lesson_slug": "01-hello-world",
  "exercises": [
    {
      "exercise_id": 1,
      "exercise_slug": "hello-print",
      "completed": true,
      "attempts": 1,
      "completed_at": "2026-07-01T12:00:00Z"
    }
  ]
}
```

---

## Health

### GET /api/health

Simple health check (no auth required).

**Response (200):**
```json
{
  "status": "ok"
}
```