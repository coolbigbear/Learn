# Lesson 25: API Authentication Methods

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand why APIs need authentication
> - Send HTTP requests with Basic Authentication
> - Use API keys to authenticate requests
> - Understand what JWT is and how to use it
> - Explain OAuth 2.0 flows at a high level
> - Include the `Authorization` header in Python (requests) and JavaScript (fetch)
> - Follow security best practices for each method

---

## Why Authenticate APIs?

An open API on the internet is like a house with no locks — anyone can walk in. Authentication answers **who you are**; authorisation answers **what you're allowed to do**.

Most public APIs require some form of authentication so they can:
- Track usage and apply rate limits
- Protect user data from unauthorised access
- Bill for paid tiers

The most common methods are:
1. **Basic Authentication** — simple username/password pair
2. **API Keys** — a single secret token
3. **JWT (JSON Web Tokens)** — encoded, self-contained tokens
4. **OAuth 2.0** — delegated authorisation framework

All of them send credentials through the **`Authorization` HTTP header**.

---

## The Authorization Header

Every authentication method covered in this lesson sends its credentials in the `Authorization` request header. The general format is:

```
Authorization: <type> <credentials>
```

The **type** tells the server what kind of auth you're using, and **credentials** is the actual secret data, formatted according to that type.

Let's look at each method one by one.

---

## 1. Basic Authentication

### How It Works

The client sends a username and password combined into a single string (`username:password`), encoded with Base64, and placed in the `Authorization` header:

```
Authorization: Basic dXNlcjpwYXNz
```

The word **Basic** is the type, and the garbled text is `user:pass` encoded with Base64.

**Important:** Base64 is **not encryption** — it's encoding. Anyone who intercepts the request can decode it instantly. Basic Auth must **always** be used over HTTPS.

### Python Example

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    "https://api.example.com/user/profile",
    auth=HTTPBasicAuth("alice", "secret123")
)
print(response.status_code)
print(response.json())
```

You can also set the header manually:

```python
import requests
import base64

credentials = base64.b64encode(b"alice:secret123").decode("utf-8")
headers = {"Authorization": f"Basic {credentials}"}

response = requests.get("https://api.example.com/user/profile", headers=headers)
```

### JavaScript Example

```javascript
const username = "alice";
const password = "secret123";
const encoded = btoa(`${username}:${password}`);

const response = await fetch("https://api.example.com/user/profile", {
  headers: {
    "Authorization": `Basic ${encoded}`
  }
});
const data = await response.json();
console.log(data);
```

### Security Notes
- **Always use HTTPS** — without it, credentials are sent in plain text
- Base64 is not a hash; it's trivially reversible
- Basic Auth sends credentials on **every request**, increasing exposure
- Avoid Basic Auth for production public APIs; prefer API keys or OAuth

---

## 2. API Keys

### How It Works

An API key is a unique string issued to a client. It's typically sent in one of two places:

**In the Authorization header:**
```
Authorization: Bearer sk-live-abc123def456
```

**Or as a query parameter:**
```
https://api.example.com/data?api_key=sk-live-abc123def456
```

The **Bearer** type means "the bearer of this token gets access" — whoever holds the key can use it. The server looks up the key to identify the client.

Sending the key in a header is **strongly preferred** over query parameters; URLs are logged by proxies, browsers, and servers, exposing the key.

### Python Example

```python
import requests

headers = {"Authorization": "Bearer sk-live-abc123def456"}
response = requests.get(
    "https://api.example.com/data",
    headers=headers
)
print(response.json())
```

### JavaScript Example

```javascript
const response = await fetch("https://api.example.com/data", {
  headers: {
    "Authorization": "Bearer sk-live-abc123def456"
  }
});
const data = await response.json();
```

### Security Notes
- **Never embed API keys in client-side code** (frontend JavaScript, mobile apps) — anyone can inspect the source
- Store keys in environment variables or a secrets manager
- Rotate keys periodically
- Use separate keys for development and production
- Prefix keys (e.g., `sk-live-`, `sk-test-`) so you can identify the environment at a glance

---

## 3. JWT (JSON Web Token)

### How It Works

A JWT is a self-contained token made of three Base64-encoded parts separated by dots:

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJhZG1pbiJ9.dGhpcyBpc...
```

**Parts of a JWT:**

| Part | Name | What it contains |
|------|------|------------------|
| Header | Algorithm & token type | `{"alg": "HS256", "typ": "JWT"}` |
| Payload | Claims (data) | `{"user_id": 123, "role": "admin", "exp": 1700000000}` |
| Signature | Verifies integrity | Created by hashing header + payload with a secret key |

The server signs the token with a secret; the client presents it as:

```
Authorization: Bearer <jwt>
```

The server verifies the signature and reads the claims. This means the server **doesn't need a database lookup** — the token itself carries the user info (stateless authentication).

### Python Example — Decoding a JWT

```python
import jwt  # PyJWT library

# Token received from the server
token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJhZG1pbiJ9.xxxx"

# Verify and decode (will raise an error if invalid or expired)
secret = "your-server-secret-key"
payload = jwt.decode(token, secret, algorithms=["HS256"])

print(payload["user_id"])  # 123
print(payload["role"])     # admin
```

### Python Example — Sending a JWT in a Request

```python
import requests

token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJhZG1pbiJ9.xxxx"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "https://api.example.com/admin/dashboard",
    headers=headers
)
print(response.json())
```

### JavaScript Example

```javascript
const token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJhZG1pbiJ9.xxxx";

const response = await fetch("https://api.example.com/admin/dashboard", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
});
const data = await response.json();
```

To decode a JWT in the browser (without verifying the signature — client-side only for reading payload):

```javascript
function parseJWT(token) {
  const payload = token.split(".")[1];
  return JSON.parse(atob(payload));
}

const decoded = parseJWT(token);
console.log(decoded.user_id); // 123
```

### Security Notes
- JWTs are **signed, not encrypted** — the payload is readable by anyone who has the token
- Store tokens **securely** — not in `localStorage` if possible (vulnerable to XSS)
- Use short expiration times (15–60 minutes) and refresh tokens for longer sessions
- Always verify the signature server-side; never trust a client-decoded JWT for authorisation

---

## 4. OAuth 2.0

### How It Works

OAuth 2.0 is a framework for **delegated authorisation** — it lets an application access resources on your behalf without seeing your password.

**Real-world analogy:** You give a valet a special key to park your car. The valet can park it but can't access the glove box. OAuth works the same way — the app gets a limited token instead of your password.

### The Participants

| Role | What it is |
|------|------------|
| **Resource Owner** | The user who owns the data |
| **Client** | The app requesting access |
| **Authorisation Server** | Issues tokens after authentication |
| **Resource Server** | Hosts the protected data (the API) |

### Common OAuth 2.0 Flows

**1. Authorisation Code Flow** (most common for web apps)

```
User → App: "Log in with Google"
App → Google: Redirects to login page
User → Google: Enters credentials
Google → App: Sends a temporary authorisation code
App → Google: Exchanges code for an access token
App → API: Requests data with access token
API → App: Returns data (if token is valid)
```

The app never sees the user's password. It gets a short-lived access token and optionally a long-lived refresh token.

**2. Client Credentials Flow** (server-to-server)

Used when two backend services talk to each other (no user involved). The client authenticates with its own client ID and secret and receives a token.

```
Service A → Auth Server: "I am service A (client_id + client_secret)"
Auth Server → Service A: "Here's your access token"
Service A → Service B API: Requests data with access token
```

### Python Example — Client Credentials Flow

```python
import requests

# Step 1: Get a token
token_response = requests.post(
    "https://auth.example.com/oauth/token",
    data={
        "grant_type": "client_credentials",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret"
    }
)
access_token = token_response.json()["access_token"]

# Step 2: Use the token
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("https://api.example.com/protected/data", headers=headers)
print(response.json())
```

### JavaScript Example — Client Credentials Flow

```javascript
// Step 1: Get a token
const tokenRes = await fetch("https://auth.example.com/oauth/token", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({
    grant_type: "client_credentials",
    client_id: "your-client-id",
    client_secret: "your-client-secret"
  })
});
const { access_token } = await tokenRes.json();

// Step 2: Use the token
const response = await fetch("https://api.example.com/protected/data", {
  headers: { "Authorization": `Bearer ${access_token}` }
});
const data = await response.json();
```

### Security Notes
- OAuth 2.0 never exposes the user's password to the client application
- Access tokens should be short-lived (minutes to hours)
- Refresh tokens are long-lived; protect them like passwords
- Always validate the `redirect_uri` in the Authorisation Code Flow
- Use PKCE (Proof Key for Code Exchange) for mobile and single-page apps
- OAuth 2.0 is an **authorisation** framework, not an **authentication** protocol; use OpenID Connect (OIDC) on top of OAuth 2.0 for authentication

---

## Common Mistakes

- **Hardcoding secrets in code** — Never write API keys, passwords, or JWT secrets directly in your source code. Use environment variables or `.env` files.
- **Using Basic Auth without HTTPS** — Base64 is encoding, not encryption. Anyone intercepting the request can read the credentials instantly.
- **Exposing API keys in client-side code** — Frontend JavaScript is visible to every user. Any API key embedded in frontend code is public.
- **Not rotating keys or tokens** — If a key is compromised, rotate it immediately. Regular rotation limits the damage of a leak.
- **Using JWTs without expiration** — A JWT without an `exp` claim never expires. If stolen, it's valid forever. Always set a short expiration (15–60 minutes).

## Best Practices

1. **Always use HTTPS** — Every authentication method in this lesson sends secrets over the wire. Without HTTPS, all of them are vulnerable to interception.
2. **Prefer Bearer tokens (API keys / JWT) over Basic Auth** — Bearer tokens can be scoped, rotated independently of user accounts, and revoked individually.
3. **Store secrets in environment variables** — Use `os.getenv("API_KEY")` or a `.env` file (with `python-dotenv`). Never commit secrets to git.
4. **Use short-lived JWTs with refresh tokens** — Access tokens expire in minutes; refresh tokens last longer and are stored more securely.
5. **Validate tokens on every request** — Server-side verification of JWTs (signature, expiration, issuer) prevents tampering and replay attacks.

---

## Comparison Table

| Method | Best For | Security Level | Complexity |
|--------|----------|---------------|------------|
| Basic Auth | Quick tests, internal tools | Low (requires HTTPS) | Very low |
| API Keys | Public API access, service accounts | Medium | Low |
| JWT | Stateless auth, single sign-on | High (when done right) | Medium |
| OAuth 2.0 | Third-party access, delegated auth | High | High |

---

## Summary

- The `Authorization` header is the standard way to send credentials to an API
- **Basic Auth** sends `Basic <base64(username:password)>` — simple but only safe over HTTPS
- **API Keys** use `Bearer <key>` in the header; keep them out of client-side code and URLs
- **JWT** is a signed, self-contained token with readable payload; verify the signature server-side
- **OAuth 2.0** lets apps access data without seeing passwords; use the right flow for your use case
- Never hard-code secrets. Use environment variables, `.env` files, or a secrets manager

### What's Next?

In the next lesson, you'll build a complete **API Capstone Project** that brings together authentication, database storage, and everything you've learned so far.
