# Lesson 17: Introduction to FastAPI

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand what a web API is and how it works
> - Install and run a FastAPI server
> - Create GET and POST endpoints
> - Use path parameters and query parameters
> - Test your API with the interactive docs

---

## What Is an API?

API stands for **Application Programming Interface**. In web development, an API is a set of rules that allows one program to talk to another over the internet using HTTP.

Think of a restaurant: you (the client) place an order (HTTP request), the kitchen (the server) prepares the food and sends it back (HTTP response).

**Common HTTP methods:**
- `GET` — Retrieve data (e.g., get a list of users)
- `POST` — Create new data (e.g., add a new user)
- `PUT` — Update existing data
- `DELETE` — Remove data

---

## What is FastAPI?

FastAPI is a modern Python web framework for building APIs. It's:
- **Fast** — high performance, on par with Node.js and Go
- **Easy** — uses Python type hints for automatic validation
- **Self-documenting** — generates interactive OpenAPI docs

Install it:

```bash
pip install fastapi uvicorn
```

---

## Your First FastAPI App

Create a file called `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
```

Run it:

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` — you'll see `{"message": "Hello, World!"}`.

Now visit `http://localhost:8000/docs` — FastAPI generated interactive documentation for you automatically!

---

## Path Parameters

You can capture parts of the URL as parameters:

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}
```

Try visiting `/items/42`. The `{item_id}` is extracted from the URL path.

---

## Query Parameters

Parameters that come after `?` in the URL:

```python
@app.get("/search")
async def search(q: str = "", limit: int = 10):
    return {"query": q, "results_count": limit}
```

Visit `/search?q=python&limit=5`.

---

## POST Endpoints with Request Body

Use Pydantic models to define the shape of incoming data:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.post("/items")
async def create_item(item: Item):
    return {"message": f"Created {item.name} for ${item.price}"}
```

Send a POST request with JSON:

```json
{"name": "Widget", "price": 9.99}
```

---

## Summary

- FastAPI makes it easy to build web APIs with Python
- `@app.get()` and `@app.post()` define endpoints
- Path parameters (`/items/{id}`) and query parameters (`?q=...`) let you accept input
- Pydantic models validate request bodies automatically
- Visit `/docs` for automatic interactive API documentation
