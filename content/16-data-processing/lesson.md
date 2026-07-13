# Lesson 16: Data Processing — CSV, JSON, and APIs

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Read and write CSV files using Python's `csv` module
> - Work with JSON data — serialize and deserialize
> - Make HTTP requests to web APIs with the `requests` library
> - Parse API responses and extract useful information

---

## Why Data Processing?

In the real world, data rarely comes in neat Python lists. It comes in **CSV files** (spreadsheets), **JSON** (web data), or from **APIs** (other services). Learning to process these formats is essential for almost any Python project.

---

## CSV Files

CSV (Comma-Separated Values) is a simple file format for tabular data. Each line is a row, and values are separated by commas:

```
name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo
```

### Reading CSV Files

```python
import csv

with open("people.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)  # Each row is a list of strings
```

Output:
```
['name', 'age', 'city']
['Alice', '25', 'New York']
['Bob', '30', 'London']
```

### CSV with Headers (Dictionary Reader)

`DictReader` uses the first row as field names and returns dictionaries:

```python
import csv

with open("people.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']} is {row['age']} years old from {row['city']}")
```

### Writing CSV Files

```python
import csv

with open("output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age", "city"])        # Header
    writer.writerow(["Alice", 25, "New York"])
    writer.writerow(["Bob", 30, "London"])
```

Using `DictWriter`:

```python
import csv

with open("output.csv", "w", newline="") as f:
    fieldnames = ["name", "age", "city"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 25, "city": "New York"})
```

---

## JSON

JSON (JavaScript Object Notation) is the most common data format for web APIs. It looks just like Python dictionaries and lists:

```json
{
  "name": "Alice",
  "age": 25,
  "hobbies": ["reading", "hiking"],
  "address": {
    "city": "New York",
    "zip": "10001"
  }
}
```

### Parsing JSON (deserialize)

```python
import json

# From a string
json_string = '{"name": "Alice", "age": 25}'
data = json.loads(json_string)     # loads = load string
print(data["name"])                 # "Alice"
print(type(data))                   # <class 'dict'>

# From a file
with open("data.json", "r") as f:
    data = json.load(f)             # load = load file
    print(data["name"])
```

### Creating JSON (serialize)

```python
import json

data = {
    "name": "Alice",
    "age": 25,
    "hobbies": ["reading", "hiking"]
}

# To a string
json_string = json.dumps(data, indent=2)  # dumps = dump string
print(json_string)

# To a file
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)          # dump = dump file
```

The `indent=2` parameter makes the output human-readable (pretty-printed).

---

## Making API Calls with `requests`

An **API** (Application Programming Interface) lets your program talk to other services over the internet. Python's `requests` library makes this simple.

First, install it:

```bash
pip install requests
```

### GET Requests

```python
import requests

response = requests.get("https://api.github.com/users/octocat")
print(response.status_code)  # 200 = success
print(response.json())       # Parse JSON response as Python dict
```

A real example — getting the current weather (using a free API):

```python
import requests

# Free public API — no key needed
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

### Working with API Data

```python
import requests

# Get public info about Python Issues (simplified example)
response = requests.get("https://api.github.com/search/repositories",
                        params={"q": "language:python", "sort": "stars"})

if response.status_code == 200:
    data = response.json()
    for repo in data["items"][:3]:
        print(f"{repo['name']}: {repo['stargazers_count']} stars")
```

---

## Putting It All Together: CSV → JSON → API

Here's a common workflow — read data from a CSV, convert it to JSON, then post it to an API:

```python
import csv
import json
import requests

# Step 1: Read CSV
users = []
with open("users.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        users.append(row)

# Step 2: Save as JSON
with open("users.json", "w") as f:
    json.dump(users, f, indent=2)

# Step 3: (Optional) Send to an API
# response = requests.post("https://api.example.com/users", json=users)
# print(response.status_code)
```

---

## Try It Yourself

1. Create a list of dictionaries representing students (name, grade) and save it as a JSON file.
2. Read that JSON file back and print each student's name and grade.
3. Write the student data to a CSV file instead of JSON.

---

## Common Mistakes

- **Forgetting to install `requests`:** It's not in the standard library! Run `pip install requests` first.
- **Not checking `status_code`:** An API might return an error without crashing your program.
- **Confusing `json.load()` and `json.loads()`:** `load` = file, `loads` = string. The 's' stands for 'string'.
- **Not handling missing keys:** API responses may not have all the fields you expect — use `.get()` or check with `in`.

---

## Summary

- **CSV** is for tabular data; use `csv.reader`, `csv.DictReader`, `csv.writer`, `csv.DictWriter`
- **JSON** is for structured data; use `json.load()`/`json.loads()` to read, `json.dump()`/`json.dumps()` to write
- **APIs** let you talk to other services; use `requests.get()` and `requests.post()`
- Always check `response.status_code` before using API data
- Install third-party libraries with `pip install`
