# Lesson 19: Handling JSON Payloads in APIs

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand what a JSON payload is in the context of HTTP requests and responses
> - Set the correct `Content-Type` and `Accept` headers for JSON communication
> - Send JSON data in POST, PUT, and PATCH requests using Python's `requests` library
> - Parse JSON responses and handle errors gracefully
> - Validate JSON structure before sending it to an API
> - Work with nested JSON objects and arrays in API payloads
> - Compare Python and JavaScript approaches to JSON API calls

---

## What Is a JSON Payload?

A **JSON payload** is the body of an HTTP request or response that carries data in JSON format. When you interact with a web API, you typically:

1. **Send** a JSON object in the request body (POST, PUT, PATCH) to create or update a resource
2. **Receive** a JSON object in the response body that tells you what happened

Here's what a typical JSON payload looks like in an HTTP exchange:

```
POST /api/users HTTP/1.1
Content-Type: application/json
Accept: application/json

{
  "name": "Alice",
  "email": "alice@example.com",
  "age": 25
}
```

The server replies:

```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "age": 25,
  "created_at": "2025-07-23T12:00:00Z"
}
```

The request body `{"name": "Alice", ...}` is the **JSON payload** — the data you're sending to the API.

---

## Setting the Right Headers

Two headers are critical when working with JSON payloads:

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Type` | `application/json` | Tells the server the request body is JSON |
| `Accept` | `application/json` | Tells the server you want a JSON response |

If you forget `Content-Type: application/json`, the server may not parse your payload correctly. Some APIs are forgiving, but most require the correct header.

---

## Sending JSON with Python's `requests` Library

Python's `requests` library makes sending JSON payloads simple. Let's start with a POST request:

### Basic POST with JSON

```python
import requests

url = "https://jsonplaceholder.typicode.com/posts"

payload = {
    "title": "My First Post",
    "body": "This is the content of my post.",
    "userId": 1
}

response = requests.post(url, json=payload)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

The magic is the `json=` parameter. When you pass a Python dictionary to `json=`, `requests` does three things automatically:

1. Converts the dict to a JSON string (`json.dumps()`)
2. Sets `Content-Type: application/json`
3. Sets `Accept: application/json`

You don't need to call `json.dumps()` yourself or set headers manually — `requests` handles it.

### Equivalent with Manual Headers

If you ever need to do it manually (sometimes APIs need custom variations):

```python
import requests
import json

url = "https://jsonplaceholder.typicode.com/posts"

payload = {"title": "Hello", "body": "World", "userId": 1}

response = requests.post(
    url,
    data=json.dumps(payload),          # Serialize manually
    headers={"Content-Type": "application/json"}
)

print(response.json())
```

But **prefer the `json=` parameter** — it's cleaner and less error-prone.

### PUT and PATCH with JSON

The same `json=` parameter works with PUT (full update) and PATCH (partial update):

```python
import requests

# PUT — replace the entire resource
put_payload = {"title": "Updated Title", "body": "New body", "userId": 1}
put_resp = requests.put(
    "https://jsonplaceholder.typicode.com/posts/1",
    json=put_payload
)
print(f"PUT status: {put_resp.status_code}")

# PATCH — update only specific fields
patch_payload = {"title": "Only Title Changed"}
patch_resp = requests.patch(
    "https://jsonplaceholder.typicode.com/posts/1",
    json=patch_payload
)
print(f"PATCH status: {patch_resp.status_code}")
```

---

## Receiving and Parsing JSON Responses

Once you get a response, use `.json()` to parse the JSON body into a Python dictionary or list:

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

# Check if the request succeeded
if response.status_code == 200:
    data = response.json()          # Parses JSON → Python dict
    print(data["title"])            # Access fields
    print(data["body"])
else:
    print(f"Error: {response.status_code}")
```

### What is `.json()`?

`.json()` calls `json.loads()` on the response body internally. It's a convenience method that:

1. Reads the response body as text
2. Parses it with `json.loads()`
3. Returns the resulting Python object (dict, list, str, etc.)

```python
# These two are equivalent:
data = response.json()

# Same as:
import json
data = json.loads(response.text)
```

### Handling Lists in Responses

Many APIs return JSON arrays at the top level:

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts")
posts = response.json()  # posts is a list of dicts

print(f"Got {len(posts)} posts")
for post in posts[:3]:   # Show first 3
    print(f"  - {post['id']}: {post['title']}")
```

---

## Working with Nested JSON Payloads

Real-world APIs frequently have nested objects and arrays. Here's a common example — a user with an address and a list of orders:

```python
import requests

# Nested payload we're sending
new_user = {
    "name": "Alice",
    "email": "alice@example.com",
    "address": {
        "street": "123 Main St",
        "city": "Springfield",
        "zip": "12345"
    },
    "tags": ["premium", "new"],
    "preferences": {
        "notifications": True,
        "theme": "dark"
    }
}

response = requests.post("https://api.example.com/users", json=new_user)
user = response.json()

# Access nested fields in the response
print(user["address"]["city"])       # "Springfield"
print(user["tags"][0])               # "premium"
print(user["preferences"]["theme"])  # "dark"
```

### Building Nested Payloads Programmatically

You don't have to write the entire nested structure by hand. Build it step by step:

```python
import requests

# Start with base info
user = {"name": "Bob", "email": "bob@example.com"}

# Add nested address
user["address"] = {
    "street": "456 Oak Ave",
    "city": "Portland",
    "zip": "97201"
}

# Add tags
user["tags"] = ["returning", "vip"]

# Add nested preferences one key at a time
user["preferences"] = {}
user["preferences"]["notifications"] = False
user["preferences"]["theme"] = "light"

response = requests.post("https://api.example.com/users", json=user)
print(response.status_code)
```

---

## Validating JSON Structure Before Sending

Before you send a payload to an API, it's wise to check that it has the required structure. Here are three common validation patterns:

### 1. Check Required Keys

```python
import requests

def validate_user_payload(payload):
    """Check that required fields exist before sending."""
    required = ["name", "email"]
    for key in required:
        if key not in payload:
            raise ValueError(f"Missing required field: '{key}'")
    return True

user = {"name": "Alice"}  # Missing "email"

try:
    validate_user_payload(user)
    response = requests.post("https://api.example.com/users", json=user)
    print(response.json())
except ValueError as e:
    print(f"Validation error: {e}")
```

### 2. Validate Data Types

```python
def validate_types(payload):
    """Ensure fields have the correct types."""
    if "age" in payload and not isinstance(payload["age"], (int, float)):
        raise TypeError(f"'age' must be a number, got {type(payload['age']).__name__}")
    if "tags" in payload and not isinstance(payload["tags"], list):
        raise TypeError(f"'tags' must be a list, got {type(payload['tags']).__name__}")
    return True

# This will pass
validate_types({"age": 25, "tags": ["a", "b"]})

# This will raise TypeError
# validate_types({"age": "twenty-five"})
```

### 3. Nested Validation

```python
def validate_address(payload):
    """Check nested address fields."""
    address = payload.get("address")
    if address is not None:
        required_address = ["street", "city"]
        for key in required_address:
            if key not in address:
                raise ValueError(f"Address missing required field: '{key}'")
    return True

user = {
    "name": "Alice",
    "address": {"street": "123 Main St"}  # Missing "city"
}

try:
    validate_address(user)
    print("Address is valid")
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Error Handling: When Things Go Wrong

### Handling HTTP Errors

The `requests` library provides `raise_for_status()` to catch HTTP errors:

```python
import requests

url = "https://jsonplaceholder.typicode.com/posts/99999"  # Likely doesn't exist

response = requests.get(url)

try:
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    data = response.json()
    print(data)
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.ConnectionError:
    print("Could not connect to the server")
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.RequestException as e:
    print(f"Something went wrong: {e}")
```

### Handling Malformed JSON Responses

Sometimes a server returns invalid JSON or a non-JSON response despite saying `Content-Type: application/json`:

```python
import requests
import json

response = requests.get("https://api.example.com/data")

try:
    data = response.json()
except json.JSONDecodeError as e:
    print(f"Server returned invalid JSON: {e}")
    print(f"Raw text: {response.text[:200]}")
```

### Handling Missing Keys in the Response

API responses can change — a field that was always present might be missing:

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
data = response.json()

# Safe access with .get()
title = data.get("title", "No title")
body = data.get("body", "No body")

# Nested safe access
address = data.get("address", {})
city = address.get("city", "Unknown")

print(f"Title: {title}")
```

### Complete Error Handling Pattern

Here's a robust pattern for API calls:

```python
import requests
import json

def fetch_post(post_id):
    """Fetch a blog post with full error handling."""
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Validate we got what we expected
        if "title" not in data:
            print("Warning: Response missing 'title' field")

        return data

    except requests.exceptions.HTTPError:
        print(f"Server returned {response.status_code}")
        try:
            error_detail = response.json()
            print(f"Error details: {error_detail}")
        except json.JSONDecodeError:
            print(f"Raw error: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the server — is it running?")
    except requests.exceptions.Timeout:
        print("Request timed out — the server may be overloaded")
    except json.JSONDecodeError:
        print(f"Invalid JSON in response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"Unexpected error: {e}")

    return None

# Test it
result = fetch_post(1)
if result:
    print(f"Fetched: {result['title']}")
```

---

## JavaScript Example: fetch API

For comparison, here's how you'd do the same thing in JavaScript. This is useful if you work with APIs from the browser or Node.js:

### Sending JSON with fetch

```javascript
// POST with JSON payload
const payload = {
  title: "My First Post",
  body: "This is the content.",
  userId: 1
};

const response = await fetch("https://jsonplaceholder.typicode.com/posts", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  body: JSON.stringify(payload)   // Serialize — like json.dumps()
});

const data = await response.json();  // Parse — like response.json()
console.log(data);
```

### Key Differences Between Python and JavaScript

| Concept | Python (`requests`) | JavaScript (`fetch`) |
|---------|-------------------|---------------------|
| Serialize | Automatic with `json=` | Manual `JSON.stringify()` |
| Parse | `.json()` method | `response.json()` |
| Set content type | Automatic with `json=` | Manual `headers: {"Content-Type": "application/json"}` |
| Error handling | `raise_for_status()` | Check `response.ok` |

---

## Common Pitfalls

### 1. Forgetting to Parse the Response

```python
# ❌ Wrong — this gives you a Response object, not the data
response = requests.get("https://api.example.com/data")
print(response)  # Prints <Response [200]>

# ✅ Correct — call .json() to parse
data = response.json()
```

### 2. Sending a String Instead of a Dict

```python
# ❌ Wrong — already-serialized string
payload = '{"name": "Alice"}'
response = requests.post(url, data=payload)

# ✅ Correct — let requests handle serialization
payload = {"name": "Alice"}
response = requests.post(url, json=payload)

# OR if you must send a string, set headers manually
response = requests.post(url, data=payload, headers={"Content-Type": "application/json"})
```

### 3. Forgetting to Set Headers with `data=` Parameter

```python
# ❌ Wrong — no Content-Type header
response = requests.post(url, data='{"name": "Alice"}')

# ✅ Correct — set headers when using data=
response = requests.post(url, data='{"name": "Alice"}',
                         headers={"Content-Type": "application/json"})
```

### 4. Assuming All Responses Are JSON

Some endpoints return `204 No Content` (no body), HTML error pages, or plain text. Always check before calling `.json()`:

```python
response = requests.delete("https://api.example.com/users/1")
if response.status_code == 204:
    print("Deleted successfully — no JSON body")
elif response.headers.get("content-type", "").startswith("application/json"):
    data = response.json()
else:
    print(f"Unexpected response: {response.text[:100]}")
```

### 5. Not Handling Nested Missing Keys

```python
data = response.json()

# ❌ This crashes if 'address' is None or missing
print(data["address"]["city"])

# ✅ Safe nested access
address = data.get("address") or {}
city = address.get("city", "Unknown")
print(city)
```

---

## Putting It All Together — A Complete API Client

Here's a complete example that creates a user with nested data, then fetches and displays the result:

```python
import requests
import json

API_BASE = "https://jsonplaceholder.typicode.com"

def create_user():
    """Create a new user with nested payload."""
    payload = {
        "name": "Alice Johnson",
        "username": "alicej",
        "email": "alice@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "zipcode": "12345"
        },
        "company": {
            "name": "Tech Corp",
            "catchPhrase": "Innovating tomorrow"
        }
    }

    try:
        response = requests.post(f"{API_BASE}/users", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create user: {e}")
        return None

def get_user(user_id):
    """Fetch a user and display nested fields safely."""
    try:
        response = requests.get(f"{API_BASE}/users/{user_id}", timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"User: {data.get('name', 'N/A')}")
        print(f"Email: {data.get('email', 'N/A')}")

        # Safe nested access
        address = data.get("address") or {}
        print(f"City: {address.get('city', 'N/A')}")

        company = data.get("company") or {}
        print(f"Company: {company.get('name', 'N/A')}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch user: {e}")

# Run it
user = create_user()
if user:
    print(f"Created user with id={user.get('id')}")
    get_user(user.get("id", 1))
```

---

## Try It Yourself

1. Send a POST request with a JSON payload using the `json=` parameter.
2. Parse a JSON response with `.json()` and access specific fields.
3. Send a PUT request with a nested JSON payload.
4. Catch and handle an HTTP 404 error from an API.
5. Validate that a payload has the required keys before sending.
6. Safely access nested fields in a JSON response using `.get()`.
7. Write a function that fetches data and handles connection errors, timeouts, and bad JSON.
8. Compare the Python `requests` approach with the JavaScript `fetch` approach for the same API call.
9. Build a nested payload programmatically and send it to an API.
10. Create a complete API client function with full error handling.

---

## Common Mistakes

- **Forgetting to call `.json()`** — you get a Response object, not the parsed data
- **Using `data=` instead of `json=`** — this sends a string without setting `Content-Type`
- **Not checking `response.status_code`** before parsing JSON
- **Assuming nested keys always exist** — API responses can change, always validate or use `.get()`
- **Catching too broadly** — don't catch all exceptions; be specific (`HTTPError`, `ConnectionError`, etc.)
- **Not setting a timeout** — an API call could hang forever without `timeout=N`

---

## Summary

- A **JSON payload** is the JSON data sent in an HTTP request or response body
- Use `Content-Type: application/json` when sending JSON and `Accept: application/json` when receiving
- Python's `requests` library: use `json=` parameter for automatic serialization and header setting
- Parse responses with `.json()` — equivalent to `json.loads(response.text)`
- Validate payloads before sending — check required keys and data types
- Handle errors at every stage: connection, HTTP status, JSON parsing, and missing keys
- Use `.get()` for safe nested access in API responses
- In JavaScript's `fetch`, you handle serialization and headers manually with `JSON.stringify()` and the `headers` option
