# Lesson 19: HTTP Requests with Path Variables and Headers

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand URL structure and the difference between path parameters and query parameters
> - Make HTTP GET and POST requests using Python's `requests` library
> - Dynamically construct URLs with path variables
> - Set HTTP headers including `Accept`, `Content-Type`, and custom headers
> - Make API requests from JavaScript using `fetch()`

---

## What Is an HTTP Request?

Before we dive in, let's quickly recap: every time your browser loads a webpage or your phone fetches data from an app, it sends an **HTTP request** to a server. The server processes it and sends back an **HTTP response**.

An HTTP request consists of:

1. **A URL** — where to send the request
2. **A method** — what to do (GET, POST, PUT, DELETE, etc.)
3. **Headers** — extra information for the server
4. **A body** (optional) — data to send to the server (used with POST, PUT)

In this lesson, you'll learn how to make HTTP requests from code, focusing on two key skills:

- **Path variables** — building dynamic URLs like `/users/42` or `/posts/5/comments`
- **Headers** — sending the right metadata with your requests

You can (and should) test the examples below against a real API. We'll use `https://jsonplaceholder.typicode.com`, a free fake API for testing.

---

## URL Structure: Static vs Dynamic

A URL like `https://api.example.com/users` is **static** — it always points to the same resource.

A URL like `https://api.example.com/users/42` is **dynamic** — the `42` is a **path parameter** (also called a **path variable**) that identifies a specific user.

The path parameter is the variable part of the URL path:

```
https://api.example.com/users/{id}
                          └────┬───┘
                         path variable
```

When you make the request, you replace `{id}` with an actual value:

| Pattern         | Actual URL              | Meaning               |
|-----------------|-------------------------|-----------------------|
| `/users/{id}`   | `/users/42`             | Get user with ID 42   |
| `/posts/{id}`   | `/posts/5/comments`     | Get comments on post 5|
| `/search/{q}`   | `/search/python`        | Search for "python"   |

### Path Parameters vs Query Parameters

Don't confuse path parameters with **query parameters** (the `?key=value` part of a URL):

- **Path parameters** are part of the URL path itself: `/users/42`
- **Query parameters** come after a `?`: `/users?role=admin&page=2`

Both let you send data to the server, but they're used differently. Path parameters identify a specific resource; query parameters filter or modify the request.

---

## Making HTTP Requests from Python

Python's `requests` library is the most popular way to make HTTP requests. It's not built-in, so install it first:

```bash
pip install requests
```

### Basic GET Request

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/users")

print(response.status_code)    # 200
print(response.headers)        # Response headers (dict-like)
print(response.json())         # Parse the response body as JSON
```

The `.json()` method parses the response body into Python objects (lists, dicts).

### Basic POST Request

```python
import requests

new_user = {"name": "Alice", "email": "alice@example.com"}

response = requests.post(
    "https://jsonplaceholder.typicode.com/users",
    json=new_user      # Automatically sets Content-Type: application/json
)

print(response.status_code)    # 201 (Created)
print(response.json())         # The created user with an ID
```

The `json=` parameter automatically:
1. Converts your Python dict to a JSON string
2. Sets the `Content-Type` header to `application/json`

---

## Dynamic URLs with Path Variables

When you need to include a variable in the URL path, you have several options.

### Option 1: f-strings (Simple & Common)

```python
import requests

user_id = 42
response = requests.get(f"https://jsonplaceholder.typicode.com/users/{user_id}")
print(response.json())
```

This is the most readable approach for simple cases. Use it when you have one or two path variables.

### Option 2: `.format()` (Multiple Variables)

```python
import requests

user_id = 42
post_id = 5
response = requests.get(
    "https://jsonplaceholder.typicode.com/users/{}/posts/{}".format(user_id, post_id)
)
print(response.json())
```

Or with named placeholders for clarity:

```python
response = requests.get(
    "https://jsonplaceholder.typicode.com/users/{user_id}/posts/{post_id}".format(
        user_id=user_id, post_id=post_id
    )
)
```

### Option 3: String Concatenation (Avoid)

```python
# Works, but harder to read — avoid this style
user_id = 42
url = "https://jsonplaceholder.typicode.com/users/" + str(user_id)
```

String concatenation is error-prone with URLs (forgetting slashes, etc.). Use f-strings or `.format()` instead.

### Option 4: Pass Path Params via `requests` (Not Recommended)

Some people try to use the `params=` argument for path parameters — **don't**. The `params=` argument only adds query parameters (`?key=value`), not path parameters. Path variables must be part of the URL string itself.

```python
# ❌ Wrong — this adds ?id=42, not /42
response = requests.get("https://jsonplaceholder.typicode.com/users", params={"id": 42})

# ✅ Correct — id is part of the URL path
response = requests.get(f"https://jsonplaceholder.typicode.com/users/{42}")
```

---

## HTTP Headers: The Hidden Context

**Headers** are key-value pairs sent with every HTTP request that provide metadata about the request. The server uses headers to understand how to process your request and how to format the response.

### Common Request Headers

| Header          | Purpose                                              | Example Value                          |
|-----------------|------------------------------------------------------|----------------------------------------|
| `Accept`        | Tells the server what data format you want back      | `application/json`                     |
| `Content-Type`  | Tells the server what format the request body is in  | `application/json`                     |
| `Authorization` | Sends credentials (API keys, tokens)                 | `Bearer eyJhbG...NiIs...`       |
| `User-Agent`    | Identifies the client making the request             | `MyApp/1.0`                            |
| `X-API-Key`     | Custom header for API authentication                 | `abc123def456`                         |

### Setting Headers in Python Requests

Pass headers as a dictionary to the `headers=` parameter:

```python
import requests

headers = {
    "Accept": "application/json",
    "User-Agent": "MyLearningApp/1.0"
}

response = requests.get(
    "https://jsonplaceholder.typicode.com/users",
    headers=headers
)

print(response.status_code)
```

---

## The `Accept` Header

The `Accept` header tells the server what response format you can handle. The most common values are:

- `application/json` — you want JSON
- `text/html` — you want HTML
- `text/plain` — you want plain text
- `application/xml` — you want XML
- `*/*` — you'll accept anything

Many modern APIs ignore this and always return JSON, but some APIs can return different formats based on what you request:

```python
import requests

# Request JSON
headers = {"Accept": "application/json"}
response = requests.get("https://api.example.com/data", headers=headers)
data = response.json()   # Parse as JSON

# Request XML (if the API supports it)
headers = {"Accept": "application/xml"}
response = requests.get("https://api.example.com/data", headers=headers)
# response.text would contain raw XML
```

---

## The `Content-Type` Header

The `Content-Type` header tells the server what format your **request body** is in. This is crucial for POST, PUT, and PATCH requests where you're sending data.

Common values:
- `application/json` — you're sending JSON
- `application/x-www-form-urlencoded` — form data (like a web form)
- `multipart/form-data` — file uploads
- `text/plain` — plain text

When you use `requests.post(url, json=data)`, the `requests` library **automatically** sets `Content-Type: application/json`. But if you use the `data=` parameter instead of `json=`, you may need to set it manually:

```python
import requests
import json

# Using json= (recommended) — Content-Type is set automatically
response = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={"title": "Hello", "body": "World", "userId": 1}
)

# Using data= with manual JSON encoding
headers = {"Content-Type": "application/json"}
response = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    data=json.dumps({"title": "Hello", "body": "World", "userId": 1}),
    headers=headers
)
```

Both approaches work, but `json=` is simpler and less error-prone. Use `data=` when you need to send data in a format other than JSON (e.g., form-encoded data).

### Sending Form Data

```python
import requests

# Send as form-encoded (like a web form submit)
response = requests.post(
    "https://httpbin.org/post",
    data={"username": "alice", "password": "secret123"}
)
# Content-Type is automatically set to application/x-www-form-urlencoded
```

---

## Custom Headers: API Keys and More

Many APIs require **custom headers** for authentication or to pass additional context. A common pattern is using an API key:

```python
import requests

headers = {
    "X-API-Key": "your-api-key-here",
    "Accept": "application/json"
}

response = requests.get(
    "https://api.example.com/protected/data",
    headers=headers
)
```

Some APIs use the `Authorization` header with a **Bearer token** (common in modern REST APIs):

```python
import requests

token = "your-authentication-token"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

response = requests.get(
    "https://api.example.com/me",
    headers=headers
)
```

Always check the API's documentation to know which headers it expects.

---

## JavaScript Example with `fetch()`

Since APIs are language-agnostic, you'll often make requests from JavaScript too. Here's how the same patterns work in the browser or Node.js:

### GET with Path Variable

```javascript
const userId = 42;

fetch(`https://jsonplaceholder.typicode.com/users/${userId}`)
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### GET with Headers

```javascript
fetch('https://jsonplaceholder.typicode.com/users', {
  headers: {
    'Accept': 'application/json',
    'X-API-Key': 'your-api-key-here'
  }
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### POST with JSON Body and Headers

```javascript
const newUser = { name: 'Alice', email: 'alice@example.com' };

fetch('https://jsonplaceholder.typicode.com/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify(newUser)
})
  .then(response => response.json())
  .then(data => console.log('Created:', data));
```

The JavaScript `fetch()` API follows the same principles:
- Dynamic URLs use template literals (backticks + `${}`) — JavaScript's version of f-strings
- Headers are passed as an object in the `headers` property
- The request body must be manually stringified with `JSON.stringify()`

---

## Putting It All Together

Here's a complete example that combines path variables, headers, and error handling in Python:

```python
import requests

def fetch_user(user_id):
    """Fetch a user by ID with proper headers and error handling."""
    try:
        response = requests.get(
            f"https://jsonplaceholder.typicode.com/users/{user_id}",
            headers={"Accept": "application/json"},
            timeout=10  # seconds
        )
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Test it
user = fetch_user(1)
if user:
    print(f"Name: {user['name']}, Email: {user['email']}")
```

Key takeaways from this example:
- **f-string** for the dynamic URL (`f"..."` with `{user_id}`)
- **headers dict** for `Accept`
- **timeout** to avoid hanging forever
- **raise_for_status()** to catch HTTP errors
- **Specific exception types** for different failure modes

---

## Summary

- **Path variables** let you build dynamic URLs. Use f-strings (Python) or template literals (JavaScript) to insert values.
- **Path parameters** are part of the URL path (`/users/42`); they differ from **query parameters** (`?page=2`).
- **The `Accept` header** tells the server what format you want back (usually `application/json`).
- **The `Content-Type` header** tells the server what format your request body is in.
- **Custom headers** (like `X-API-Key` or `Authorization`) are used for authentication and passing extra context.
- Python's `requests` library and JavaScript's `fetch()` follow the same patterns for dynamic URLs and headers.

### What's Next?

Now that you know how to make HTTP requests from code, you're ready to build your own APIs! In the next lesson, you'll use FastAPI to create server-side endpoints that receive path parameters and headers.
