# Lesson 17: JSON Processing

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Parse JSON strings and files into Python dictionaries and lists
> - Serialize Python objects into JSON format
> - Read and write JSON files
> - Pretty-print JSON for readability

---

## What is JSON?

JSON (JavaScript Object Notation) is the most common data format used by web APIs and configuration files. It looks just like Python dictionaries and lists:

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

JSON is language-independent — almost every programming language can read and write it.

---

## Parsing JSON (Deserialize)

Python's built-in `json` module converts JSON into Python data structures.

### From a String

```python
import json

json_string = '{"name": "Alice", "age": 25}'
data = json.loads(json_string)     # loads = load string
print(data["name"])                 # "Alice"
print(type(data))                   # <class 'dict'>
```

### From a File

```python
import json

with open("data.json", "r") as f:
    data = json.load(f)             # load = load file
    print(data["name"])
```

The rule is simple: `loads` = load **s**tring, `load` = load **f**ile.

### JSON Type Mapping

| JSON | Python |
|------|--------|
| `"string"` | `str` |
| `123` | `int` |
| `1.5` | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |
| `[...]` | `list` |
| `{...}` | `dict` |

---

## Creating JSON (Serialize)

Going the other direction — Python → JSON:

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

The `indent=2` parameter makes the output human-readable (pretty-printed). Without it, the JSON is all on one line.

---

## Working with Nested JSON

Real-world JSON often has nested objects and arrays:

```python
import json

data = json.loads('{"users": [{"name": "Alice", "scores": [90, 85]}, {"name": "Bob", "scores": [78, 92]}]}')

for user in data["users"]:
    avg_score = sum(user["scores"]) / len(user["scores"])
    print(f"{user['name']}: average score = {avg_score}")
```

Output:
```
Alice: average score = 87.5
Bob: average score = 85.0
```

---

## Common JSON Mistakes

- **JSON requires double quotes:** `{"name": "Alice"}` is valid. `{'name': 'Alice'}` is NOT valid JSON (Python accepts single quotes, but JSON doesn't).
- **Trailing commas:** JSON does not allow trailing commas. `[1, 2, 3,]` is invalid.
- **Confusing `load` vs `loads`:** `load` = file, `loads` = string. The 's' stands for 'string'.
- **Forgetting `indent`:** Without it, JSON output is a single line — hard to read for humans.

---

## Try It Yourself

1. Create a dictionary representing a book (title, author, year, genres as a list)
2. Convert it to a JSON string and print it with `indent=2`
3. Write the JSON to a file called `book.json`
4. Read the file back and print the author's name

---

## Summary

- **JSON** is a text format for structured data, used everywhere in web development
- **`json.loads()`** parses a JSON **string** → Python object
- **`json.load()`** reads a JSON **file** → Python object
- **`json.dumps()`** converts Python → JSON **string**
- **`json.dump()`** writes Python → JSON **file**
- Use `indent=2` for human-readable output
- Remember: `loads`/`dumps` — the 's' means string
