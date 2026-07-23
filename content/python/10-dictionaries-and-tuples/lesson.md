# Lesson 10: Dictionaries and Tuples

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Create and work with dictionaries (key-value pairs)
> - Access, add, and modify dictionary entries
> - Understand tuples and their immutability
> - Use the `in` operator with dictionaries and tuples

---

## Dictionaries — Key-Value Pairs

A **dictionary** stores pairs of **keys** and **values**. Think of it like a real dictionary: you look up a word (the key) and get its definition (the value).

Create a dictionary with curly braces `{}` using `key: value` pairs:

```python
person = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}

print(person["name"])  # Alice
print(person["age"])   # 25
```

### Rules for Keys

- Keys must be **unique** (no duplicates)
- Keys must be **immutable** types: strings, numbers, or tuples (not lists)
- Most commonly, keys are strings

### Accessing Values

```python
# Square bracket access
print(person["name"])   # Alice

# .get() — safer, returns None if key doesn't exist
print(person.get("name"))     # Alice
print(person.get("country"))  # None
print(person.get("country", "Unknown"))  # Unknown (with default)
```

The `.get()` method is safer than `[]` because it doesn't crash when a key is missing.

### Adding and Changing Values

```python
person = {"name": "Alice", "age": 25}

# Add a new key-value pair
person["city"] = "London"

# Change an existing value
person["age"] = 26

print(person)  # {"name": "Alice", "age": 26, "city": "London"}
```

### Removing Keys

```python
# Remove a specific key
del person["city"]

# Remove and get the value
age = person.pop("age")
print(age)  # 26
```

### Looping Through a Dictionary

```python
person = {"name": "Alice", "age": 25, "city": "New York"}

# Loop through keys
for key in person:
    print(key)

# Loop through values
for value in person.values():
    print(value)

# Loop through both
for key, value in person.items():
    print(f"{key}: {value}")
```

Output:

```
name
age
city
Alice
25
New York
name: Alice
age: 25
city: New York
```

---

## The `in` Operator

The `in` operator checks whether a key exists in a dictionary:

```python
person = {"name": "Alice", "age": 25}

print("name" in person)     # True
print("city" in person)     # False
```

It also works with lists, strings, and tuples:

```python
print("a" in "hello")          # False
print(3 in [1, 2, 3, 4])      # True
print("cat" in ("dog", "cat")) # True
```

---

## Tuples — Immutable Sequences

A **tuple** is like a list you can't change. Use parentheses `()`:

```python
point = (3, 5)
colors = ("red", "green", "blue")
mixed = (1, "hello", 3.14)
```

### Why Use Tuples?

- **Immutable** — once created, you can't add, remove, or change elements. This makes them safe for data that shouldn't change.
- **Faster** than lists for fixed data.
- **Hashable** — they can be used as dictionary keys (lists cannot).

```python
# This works — tuple as a dictionary key
locations = {
    (40.7128, -74.0060): "New York",
    (51.5074, -0.1278): "London"
}

# This would crash — list as a key
# locations = {[40.7128, -74.0060]: "New York"}  # TypeError!
```

### Accessing Tuple Elements

Same as lists — use indexes:

```python
point = (3, 5)
print(point[0])  # 3
print(point[1])  # 5
```

### Tuple Unpacking

You can "unpack" a tuple into multiple variables:

```python
point = (3, 5)
x, y = point
print(f"x={x}, y={y}")  # x=3, y=5

# Works with any sequence
name, age, city = ("Bob", 30, "Paris")
```

This also works with lists and is often used with functions that return multiple values.

---

## When to Use Each

| Type | Ordered? | Mutable? | Allows Duplicates? | Use Case |
|------|----------|----------|-------------------|----------|
| List `[]` | Yes | Yes | Yes | Collection of items that may change |
| Tuple `()` | Yes | No | Yes | Fixed data, dictionary keys |
| Dict `{}` | Yes (3.7+) | Yes | Unique keys | Mapping relationships |

---

## Try It Yourself

1. Create a dictionary representing a book with keys: `title`, `author`, `year`. Print the author's name.
2. Create a tuple with 3 coordinates and unpack them into three variables.
3. Use the `in` operator to check if "email" is a key in your dictionary.

---

## Summary

- Dictionaries store key-value pairs, accessed with `dict["key"]` or `.get()`
- Keys must be unique and immutable
- Tuples are immutable sequences — once created, they can't change
- Tuple unpacking assigns each element to a variable
- `in` checks for key existence in dictionaries and membership in sequences
