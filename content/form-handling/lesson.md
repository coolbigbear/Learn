# Lesson 22: Form Handling in APIs

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand the difference between URL-encoded and multipart form data
> - Receive form data in FastAPI using `Form()`
> - Accept file uploads with `File()` and `UploadFile`
> - Send form data and files using the `requests` library
> - Validate form inputs and handle errors gracefully
> - Build a complete profile upload endpoint

---

## What Are HTML Forms?

When a web browser submits a form — a login page, a registration form, or a file upload — it sends the data as a **form submission**. There are two common encoding types:

| Encoding | Content-Type | Use Case |
|---|---|---|
| `application/x-www-form-urlencoded` | Key-value pairs like URL query strings | Text fields, checkboxes, selects |
| `multipart/form-data` | Each field is a separate MIME part with its own headers | File uploads, mixed text + files |

> **Key insight:** If your form includes a file input (`<input type="file">`), the browser **must** use `multipart/form-data`. URL-encoded forms cannot carry binary data.

---

## URL-Encoded Forms in Depth

In a URL-encoded form, the data is sent as key=value pairs separated by `&` — exactly like a URL query string, but in the request body:

```
username=jdoe&email=jane%40example.com&role=student
```

Each value is URL-encoded (spaces become `+`, special characters become `%XX`). This is the default for HTML forms.

---

## Receiving Form Data in FastAPI

FastAPI provides `Form()` to read individual form fields. It works like `Query()` and `Path()` but reads from the request body instead of the URL.

### Installation

If you haven't already, install `python-multipart` — FastAPI needs it to parse form data:

```bash
pip install python-multipart
```

### Basic Form Endpoint

```python
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/login")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username, "logged_in": True}
```

Try it with curl:

```bash
curl -X POST http://localhost:8000/login \
  -d "username=alice&password=secret123"
```

Or use the `/docs` interactive page — FastAPI generates form fields automatically.

### Form Fields with Defaults and Validation

`Form()` accepts the same parameters as `Query()`:

```python
from typing import Annotated
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/register")
async def register(
    username: str = Form(min_length=3, max_length=20),
    email: str = Form(),
    age: int = Form(ge=13, le=120),
    referrer: str = Form(default="direct")
):
    return {
        "username": username,
        "email": email,
        "age": age,
        "referrer": referrer
    }
```

You can also use `Annotated` for cleaner syntax:

```python
from typing import Annotated
from fastapi import Form

@app.post("/register")
async def register(
    username: Annotated[str, Form(min_length=3, max_length=20)],
    email: Annotated[str, Form()],
    age: Annotated[int, Form(ge=13, le=120)],
):
    ...
```

### Optional Form Fields

```python
from typing import Optional

@app.post("/contact")
async def contact(
    name: str = Form(),
    message: str = Form(),
    phone: Optional[str] = Form(default=None)
):
    ...
```

---

## Multipart Forms and File Uploads

When you need to upload files, switch to `multipart/form-data`. FastAPI uses `File()` and `UploadFile` for this.

### The `UploadFile` Type

`UploadFile` offers several advantages over raw bytes:

- **Metadata:** `filename`, `content_type`, `size`
- **Async I/O:** `await file.read()`, `await file.write()`, `await file.seek()`
- **Memory efficient:** large files are streamed, not loaded entirely into memory

### File Upload Endpoint

```python
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File()):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }
```

Test with curl:

```bash
curl -X POST http://localhost:8000/upload/ \
  -F "file=@photo.jpg"
```

### Saving an Uploaded File

Usually you'll want to save the file to disk:

```python
@app.post("/upload/save/")
async def save_uploaded_file(file: UploadFile = File()):
    # Save to disk
    with open(f"uploads/{file.filename}", "wb") as f:
        content = await file.read()
        f.write(content)
    return {"message": f"Saved {file.filename}"}
```

> **Practical tip:** In production, you'd rename files to avoid collisions and validate file types/extensions before saving.

### Multiple Files

```python
from typing import list

@app.post("/upload/multiple/")
async def upload_multiple(files: list[UploadFile] = File()):
    results = []
    for file in files:
        contents = await file.read()
        results.append({
            "filename": file.filename,
            "size": len(contents)
        })
    return {"files": results}
```

### Mixing Form Fields and Files

You can combine regular form fields with file uploads in the same endpoint:

```python
@app.post("/profile/")
async def create_profile(
    name: str = Form(),
    bio: str = Form(max_length=500),
    avatar: UploadFile = File()
):
    # Save the avatar
    avatar_bytes = await avatar.read()
    
    return {
        "name": name,
        "bio": bio,
        "avatar_filename": avatar.filename,
        "avatar_size": len(avatar_bytes)
    }
```

Test with curl:

```bash
curl -X POST http://localhost:8000/profile/ \
  -F "name=Alice" \
  -F "bio=Python developer" \
  -F "avatar=@avatar.png"
```

---

## Validating Form Data

Form data needs the same care as JSON payloads. Here are common patterns:

### Type Validation

FastAPI automatically converts form fields based on type hints:

```python
@app.post("/order")
async def place_order(
    item_id: int = Form(ge=1),      # must be integer >= 1
    quantity: int = Form(ge=1, le=100),  # between 1 and 100
    coupon: str = Form(default="", min_length=0, max_length=20)
):
    ...
```

### File Type Checking

```python
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

@app.post("/upload/avatar/")
async def upload_avatar(file: UploadFile = File()):
    # Check content type
    if file.content_type not in ALLOWED_TYPES:
        return {"error": "Only JPG, PNG, and GIF files are allowed"}
    
    # Check size
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        return {"error": "File too large — maximum 5 MB"}
    
    return {
        "message": "Avatar uploaded successfully",
        "filename": file.filename,
        "size": len(contents)
    }
```

### Using Pydantic for Form Data

While `Form()` works with individual parameters, you can also validate form data through Pydantic models by reading the raw form and parsing it:

```python
from pydantic import BaseModel, Field, EmailStr

class ProfileForm(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    age: int = Field(ge=13, le=120)

@app.post("/profile/pydantic/")
async def create_profile_pydantic(
    username: str = Form(),
    email: str = Form(),
    age: int = Form()
):
    # Validate with Pydantic
    form_data = ProfileForm(username=username, email=email, age=age)
    return form_data.model_dump()
```

> **Note:** FastAPI 0.110+ supports `Form()` with Pydantic models directly. Check your FastAPI version for the latest syntax.

---

## Sending Form Data with `requests`

Your API will often need to call other APIs or send form data as a client. Python's `requests` library handles both form types.

### URL-Encoded Form (data=)

Use the `data` parameter to send a URL-encoded form:

```python
import requests

# As a dictionary
response = requests.post(
    "http://localhost:8000/login",
    data={"username": "alice", "password": "secret123"}
)

# As a raw string
response = requests.post(
    "http://localhost:8000/login",
    data="username=alice&password=secret123"
)
```

### Multipart Form with Files (files=)

Use the `files` parameter to upload files:

```python
import requests

# Single file
with open("photo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload/",
        files={"file": f}
    )

# With filename and content type
with open("photo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload/",
        files={"file": ("photo.jpg", f, "image/jpeg")}
    )
```

### Mixed Form Fields + Files

```python
import requests

with open("avatar.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/profile/",
        data={"name": "Alice", "bio": "Python developer"},
        files={"avatar": ("avatar.png", f, "image/png")}
    )
```

> **Important:** When you mix `data` and `files`, `requests` automatically sets the Content-Type to `multipart/form-data`.

---

## Complete Example: User Registration API

Let's put everything together in a complete example:

```python
# registration.py
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
import os

app = FastAPI(title="User Registration API")

# Ensure upload directory exists
os.makedirs("uploads/avatars", exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB

@app.post("/register")
async def register_user(
    username: str = Form(min_length=3, max_length=30),
    email: str = Form(),
    password: str = Form(min_length=8),
    age: int = Form(ge=13, le=120),
    avatar: UploadFile = File()
):
    # Validate file extension
    ext = os.path.splitext(avatar.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Avatar must be one of: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    contents = await avatar.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Avatar must be under 2 MB"
        )
    
    # Save avatar (in production, use a unique filename)
    avatar_path = f"uploads/avatars/{avatar.filename}"
    with open(avatar_path, "wb") as f:
        f.write(contents)
    
    return {
        "message": f"User {username} registered successfully",
        "username": username,
        "email": email,
        "age": age,
        "avatar": avatar_path
    }
```

Test it with curl:

```bash
curl -X POST http://localhost:8000/register \
  -F "username=alice" \
  -F "email=alice@example.com" \
  -F "password=securePass123" \
  -F "age=25" \
  -F "avatar=@avatar.jpg"
```

---

## Common Pitfalls

### 1. Missing `python-multipart`

If you try to use `Form()` or `File()` without installing `python-multipart`, FastAPI raises an error:

```
RuntimeError: Form data requires "python-multipart" to be installed.
```

**Fix:** `pip install python-multipart`

### 2. Forgetting `await` for `UploadFile.read()`

`UploadFile.read()` is an async method — you must `await` it:

```python
# Wrong — returns a coroutine, not bytes
contents = file.read()

# Correct
contents = await file.read()
```

### 3. Re-reading an `UploadFile`

After calling `await file.read()`, the file stream is consumed. If you need the contents again, either store them in a variable or seek back:

```python
contents = await file.read()

# Later — if you need to read again:
await file.seek(0)
contents_again = await file.read()
```

### 4. Mixing `data` and `json` in `requests`

When calling external APIs, don't mix form data and JSON in the same request:

```python
# Wrong — requests will not encode correctly
requests.post(url, data={"key": "value"}, json={"other": "data"})

# Correct — pick one:
requests.post(url, data={"key": "value"})
requests.post(url, json={"key": "value"})
```

---

## Summary

- **URL-encoded forms** (`application/x-www-form-urlencoded`) are for text-only fields
- **Multipart forms** (`multipart/form-data`) are required for file uploads
- FastAPI's `Form()` extracts individual form fields with validation
- `File()` and `UploadFile` handle file uploads with async streaming
- Always validate file types and sizes on the server side
- Use `requests.post(url, data=...)` for URL-encoded and `requests.post(url, files=...)` for multipart
- You can mix `data` and `files` in requests to send form fields alongside uploads

**Next up:** Learn how to work with databases in your FastAPI application!
