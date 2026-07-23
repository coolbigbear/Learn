# Lesson 20: HTTP Response Codes

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand the five classes of HTTP response codes (1xx–5xx)
> - Identify and use the most common status codes: 200, 201, 204, 301, 400, 401, 403, 404, 429, 500
> - Check response status codes programmatically in Python and JavaScript
> - Handle errors gracefully using status code checks and retry patterns
> - Apply status codes correctly when building your own APIs

---

## Why This Matters

When you visit a website, your browser sends a request and the server replies with a three-digit code. `200` means "everything worked." `404` means "page not found." These codes are the **language of the web** — they tell you instantly whether a request succeeded, failed, or needs more work.

Understanding HTTP status codes is essential for:
- **Debugging** — when an API call fails, the status code tells you why
- **Building APIs** — your endpoints return the right code for every situation
- **User experience** — showing the right error message at the right time

Let's learn the codes, what they mean, and how to handle them in code.

---

## Status Code Classes

HTTP status codes are grouped into five classes. The first digit tells you the general category:

| Class | Range | Meaning | Example |
|-------|-------|---------|---------|
| **1xx** | 100–199 | Informational | 102 Processing |
| **2xx** | 200–299 | Success | 200 OK |
| **3xx** | 300–399 | Redirection | 301 Moved Permanently |
| **4xx** | 400–499 | Client Error | 404 Not Found |
| **5xx** | 500–599 | Server Error | 500 Internal Server Error |

---

## 2xx Success — Everything Worked

These are the codes you want to see. They mean the server understood the request and processed it successfully.

### 200 OK

The standard success response. The request completed and the response body contains the requested data.

**Typical use:** GET requests that return data.

```bash
$ curl https://jsonplaceholder.typicode.com/posts/1
```

```json
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "quia et suscipit..."
}
```

### 201 Created

The request succeeded and a new resource was created. Used with POST requests.

**Typical use:** Creating a new user, task, or order.

```bash
$ curl -X POST https://jsonplaceholder.typicode.com/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "New Post", "body": "Content", "userId": 1}'
```

```json
{"id": 101, "title": "New Post", "body": "Content", "userId": 1}
```

### 204 No Content

The request succeeded but there's nothing to return. The response body is empty.

**Typical use:** DELETE operations, or updates where you don't need a response body.

```bash
$ curl -X DELETE https://jsonplaceholder.typicode.com/posts/1 -w "\n%{http_code}\n"
```

```
HTTP/2 204
```

---

## 3xx Redirection — Look Over Here

The server isn't sending the resource directly — it's telling the client to look somewhere else.

### 301 Moved Permanently

The resource has a new permanent URL. All future requests should use the new URL.

### 304 Not Modified

The resource hasn't changed since the last request. The browser uses its cached copy. This saves bandwidth — the response body is empty.

You don't typically handle 3xx codes manually — your HTTP client (browser, `requests`, `fetch`) follows redirects automatically.

---

## 4xx Client Error — You Messed Up

The request contains bad data, missing authentication, or asks for something that doesn't exist. The problem is on the client side.

### 400 Bad Request

The server couldn't understand the request — usually because of malformed syntax or invalid fields.

**Common causes:** Invalid JSON, missing required fields, wrong data types.

```python
import requests

# Missing required field
response = requests.post(
    "https://api.example.com/users",
    json={"name": "Alice"}  # Missing 'email' field
)

if response.status_code == 400:
    print("Bad request — check your payload structure")
    print(response.json())  # Usually contains error details
```

### 401 Unauthorized

You need to authenticate first. Either you didn't send credentials, or they were invalid.

```python
import requests

response = requests.get("https://api.example.com/protected-data")

if response.status_code == 401:
    print("Authentication required — add your API key or token")
```

### 403 Forbidden

You're authenticated, but you don't have permission to access this resource. The server knows who you are, but you're not allowed.

**Distinction:** 401 means "who are you?", 403 means "you can't do that."

### 404 Not Found

The resource doesn't exist at that URL. This is the most famous HTTP status code.

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts/99999")

if response.status_code == 404:
    print("Resource not found — check the URL or ID")
```

### 429 Too Many Requests

You've sent too many requests in a given amount of time. The server is rate-limiting you.

```python
import requests
import time

response = requests.get("https://api.example.com/data")

if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 5))
    print(f"Rate limited. Waiting {retry_after} seconds...")
    time.sleep(retry_after)
    # Retry the request
```

---

## 5xx Server Error — The Server Messed Up

The request was probably valid, but the server encountered an error. These are (usually) not your fault.

### 500 Internal Server Error

A generic error on the server. Something went wrong, but the server didn't give details.

**Common causes:** Database connection failure, unhandled exception, misconfiguration.

### 502 Bad Gateway

The server was acting as a gateway or proxy and got an invalid response from the upstream server.

**Common cause:** A load balancer can't reach the backend application.

### 503 Service Unavailable

The server is temporarily overloaded or down for maintenance. Try again later.

```python
import requests
import time

response = requests.get("https://api.example.com/data")

if response.status_code == 503:
    print("Service temporarily unavailable. Retrying in 10 seconds...")
    time.sleep(10)
    response = requests.get("https://api.example.com/data")
```

---

## Checking Status Codes Programmatically

### Python with the `requests` Library

#### Using `status_code`

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

# Direct comparison with integer
if response.status_code == 200:
    print("Success!")
elif response.status_code == 404:
    print("Not found")
elif response.status_code >= 500:
    print("Server error")
```

#### Using `response.ok`

The `.ok` property is `True` for any 2xx status code:

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

if response.ok:
    data = response.json()
    print(f"Got post: {data['title']}")
else:
    print(f"Request failed with status {response.status_code}")
```

#### Using `raise_for_status()`

The cleanest pattern — it raises an exception for 4xx and 5xx codes:

```python
import requests

try:
    response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    data = response.json()
    print(data["title"])
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
except requests.exceptions.ConnectionError:
    print("Could not connect to server")
```

### JavaScript with the `fetch` API

```javascript
const response = await fetch("https://jsonplaceholder.typicode.com/posts/1");

// Check status code directly
if (response.status === 200) {
  const data = await response.json();
  console.log(data.title);
} else if (response.status === 404) {
  console.log("Not found");
}

// Check if successful (2xx)
if (response.ok) {
  const data = await response.json();
  console.log("Success:", data);
} else {
  console.error(`Error ${response.status}: ${response.statusText}`);
}
```

---

## Advanced: Retry Logic with Status Codes

When you get a 429 (rate limited), 503 (unavailable), or 502 (bad gateway), retrying after a delay often works.

```python
import requests
import time

def fetch_with_retry(url, max_retries=3):
    """Fetch a URL with retry logic for transient errors."""
    for attempt in range(max_retries):
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()

        if response.status_code in (429, 502, 503):
            wait = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
            print(f"Got {response.status_code}, retrying in {wait}s...")
            time.sleep(wait)
        else:
            # Non-retryable error (400, 401, 403, 404, 500)
            print(f"Non-retryable error: {response.status_code}")
            response.raise_for_status()

    print(f"Failed after {max_retries} retries")
    return None

# Test it
result = fetch_with_retry("https://jsonplaceholder.typicode.com/posts/1")
if result:
    print(f"Title: {result['title']}")
```

---

## Try It Yourself

1. Make a GET request to `https://jsonplaceholder.typicode.com/posts/99999` and check the status code. What do you get?
2. Make a POST request to the same endpoint _without_ the `Content-Type` header. Does it still succeed?
3. Modify the retry example above to use a maximum delay of 10 seconds instead of exponential backoff.
4. Visit an API that requires authentication (like GitHub's API without a token) and observe the 401 response.

---

## Common Mistakes

- **Checking only for `200`** — Some APIs return `201` for creation or `204` for deletion. Always check for the entire 2xx range with `response.ok`.
- **Forgetting to check the status code at all** — If you call `response.json()` on a 404 response that returns HTML, you'll get a `json.JSONDecodeError`.
- **Treating 4xx and 5xx the same** — A 400 (bad request) means _you_ sent bad data; a 500 (server error) means _the server_ broke. The fix is different.
- **Not handling 429 rate limits** — If you ignore rate limits, your IP or API key may be permanently banned.
- **Assuming 3xx codes are errors** — Redirects are normal. `requests` and `fetch` follow them automatically.

---

## Best Practices

1. **Always check `response.ok` or `raise_for_status()`** — Don't assume a request succeeded without verifying.
2. **Use specific status code checks for API logic** — `if status == 201` to confirm creation, `if status == 204` to confirm deletion.
3. **Implement retry logic for 5xx and 429** — These are transient. Use exponential backoff to be a good API citizen.
4. **Log the status code and response body** — When debugging, print or log `response.status_code` and `response.text` to see error details.
5. **Use the right status codes in your own APIs** — Return `201` for creation, `204` for deletion, `400` for bad input, `404` for missing resources.

---

## Summary

- HTTP status codes are grouped into five classes: 1xx (info), 2xx (success), 3xx (redirection), 4xx (client error), 5xx (server error)
- **200 OK**, **201 Created**, and **204 No Content** are the most common success codes
- **400 Bad Request**, **401 Unauthorized**, **403 Forbidden**, **404 Not Found**, and **429 Too Many Requests** are the most common client errors
- **500 Internal Server Error**, **502 Bad Gateway**, and **503 Service Unavailable** are the most common server errors
- Use `response.ok` (Python) or `response.ok` (JavaScript) to check for success, and implement retry logic for transient 5xx/429 errors

### What's Next?

Now that you understand status codes, the next lesson will dive into working with JSON payloads in API requests and responses.
