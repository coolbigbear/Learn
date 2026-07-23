# Lesson 18: Data Processing Libraries

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Use the `requests` library to fetch data from web APIs
> - Process and transform data between CSV, JSON, and Python formats
> - Understand when to use Python's standard library vs. third-party packages
> - Build a simple data pipeline from API to structured output

---

## Why Data Processing Libraries?

Python's standard library includes powerful modules like `csv` and `json` for common data formats. But for real-world data tasks — fetching data from the internet, manipulating large datasets, or doing scientific computing — you'll reach for **third-party libraries**.

In this lesson, we'll focus on two libraries that every Python developer should know:

| Library | Purpose | Built-in? |
|---------|---------|-----------|
| `csv` | Read/write CSV files | ✅ Yes (stdlib) |
| `json` | Parse/generate JSON | ✅ Yes (stdlib) |
| `requests` | Make HTTP requests | ❌ Install with `pip` |

---

## Installing Third-Party Libraries

Python's package manager `pip` installs libraries from the Python Package Index (PyPI):

```bash
pip install requests
```

Once installed, you import it like any other module:

```python
import requests
```

If you get a `ModuleNotFoundError`, it means the library isn't installed. This is a common pitfall when sharing code — always include installation instructions.

---

## Making API Calls with `requests`

An **API** (Application Programming Interface) lets your program talk to other services over the internet. The `requests` library makes this simple.

### GET Requests

```python
import requests

response = requests.get("https://api.github.com/users/octocat")
print(response.status_code)  # 200 = success
print(response.json())       # Parse JSON response as Python dict
```

A real example — fetching repository info:

```python
import requests

response = requests.get("https://api.github.com/repos/python/cpython")
if response.status_code == 200:
    data = response.json()
    print(f"Stars: {data['stargazers_count']}")
    print(f"Description: {data['description']}")
else:
    print(f"Request failed with status {response.status_code}")
```

### Checking Response Status

Always check the status code before using the data:

```python
response = requests.get("https://api.example.com/data")
if response.status_code == 200:
    data = response.json()
    # Process data
elif response.status_code == 404:
    print("Resource not found!")
elif response.status_code == 500:
    print("Server error!")
```

Common status codes: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error).

---

## Building a Data Processing Pipeline

The real power comes from combining libraries. Here's a common workflow — fetch data from an API, process it, and save it in different formats:

```python
import csv
import json
import requests

# Step 1: Fetch data from an API
response = requests.get("https://api.github.com/search/repositories",
                        params={"q": "language:python", "sort": "stars"})

if response.status_code == 200:
    data = response.json()

    # Step 2: Extract what we need
    repos = []
    for repo in data["items"][:5]:
        repos.append({
            "name": repo["name"],
            "stars": repo["stargazers_count"],
            "language": repo["language"]
        })

    # Step 3: Save as JSON
    with open("top-repos.json", "w") as f:
        json.dump(repos, f, indent=2)

    # Step 4: Save as CSV
    with open("top-repos.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "stars", "language"])
        writer.writeheader()
        writer.writerows(repos)

    print("Data saved in both JSON and CSV formats!")
```

This pattern — **fetch → transform → save** — is the foundation of virtually every data processing task.

---

## Going Further: pandas and NumPy

For serious data work, the Python ecosystem offers specialized libraries:

- **NumPy** — numerical computing with arrays and matrices
- **pandas** — data analysis with DataFrames (like spreadsheets in Python)
- **matplotlib** — data visualization and charts

Here's a preview of what pandas can do:

```python
# This is just a preview — install with: pip install pandas
import pandas as pd

# Read CSV directly into a DataFrame
df = pd.read_csv("data.csv")
print(df.head())           # First 5 rows
print(df["age"].mean())    # Average age
print(df.groupby("city").size())  # Count by city
```

You don't need to master these yet — they're covered in the Machine Learning path later. For now, remember that Python's standard library (`csv`, `json`, `sqlite3`) handles most everyday tasks, and `requests` connects you to the wider web.

---

## Choosing the Right Tool

| Task | Library |
|------|---------|
| Read/write simple CSV | `csv` (stdlib) |
| Parse/generate JSON | `json` (stdlib) |
| Fetch data from a URL | `requests` (third-party) |
| Large dataset analysis | `pandas` (third-party) |
| Numerical computation | `numpy` (third-party) |
| Charts and plots | `matplotlib` (third-party) |

---

## Common Mistakes

- **Forgetting to install `requests`:** Run `pip install requests` before importing it.
- **Not checking `status_code`:** An API might return an error without crashing your program.
- **Confusing `json.load()` and `json.loads()`:** `load` = file, `loads` = string.
- **Not handling missing keys:** API responses may not have all fields you expect — use `.get()` or check with `in`.

---

## Try It Yourself

1. Use `requests.get()` to fetch data from a public API (try `https://api.github.com/repos/python/cpython`)
2. Check the status code
3. Print two interesting fields from the JSON response
4. Save the repository name and description to a JSON file

---

## Summary

- **Standard library** (`csv`, `json`) handles common data formats with no extra installs
- **`requests`** is the go-to library for HTTP API calls (install with `pip install requests`)
- Always check `response.status_code` before using API data
- Combine libraries to build powerful **data pipelines**: fetch → transform → save
- For advanced work, **pandas**, **NumPy**, and **matplotlib** are Python's data science power trio
