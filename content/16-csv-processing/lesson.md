# Lesson 16: CSV Processing

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Read CSV files using Python's `csv` module
> - Write data to CSV files
> - Use `DictReader` and `DictWriter` for dictionary-based CSV access
> - Handle common CSV edge cases (headers, delimiters)

---

## What is CSV?

CSV (Comma-Separated Values) is a simple file format for tabular data. Each line is a row, and values are separated by commas:

```
name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo
```

CSV is one of the most common data exchange formats because it's readable by both humans and programs (Excel, databases, Python scripts).

---

## Reading CSV Files

Python's built-in `csv` module makes reading CSV files straightforward:

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

Notice that the first row (the header) is included as data. Each row is a **list of strings**, even if the values look like numbers.

---

## CSV with Headers (Dictionary Reader)

`DictReader` uses the first row as field names and returns dictionaries instead of lists. This is much more readable:

```python
import csv

with open("people.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']} is {row['age']} years old from {row['city']}")
```

Output:
```
Alice is 25 years old from New York
Bob is 30 years old from London
Charlie is 35 years old from Tokyo
```

With `DictReader`, you access columns by their header name instead of numeric index — your code becomes self-documenting.

---

## Writing CSV Files

### Using `csv.writer`

```python
import csv

with open("output.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age", "city"])        # Header
    writer.writerow(["Alice", 25, "New York"])
    writer.writerow(["Bob", 30, "London"])
```

**Important:** Always use `newline=""` when writing CSV files in Python. This prevents extra blank lines on Windows.

### Using `csv.DictWriter`

```python
import csv

with open("output.csv", "w", newline="") as f:
    fieldnames = ["name", "age", "city"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 25, "city": "New York"})
```

`DictWriter` ensures your columns stay in the order specified by `fieldnames`, even if the dictionary keys are in a different order.

---

## Choosing Your CSV Approach

| Task | Use |
|---|---|
| Read CSV as lists | `csv.reader` |
| Read CSV as dicts (with headers) | `csv.DictReader` |
| Write CSV from lists | `csv.writer` |
| Write CSV from dicts | `csv.DictWriter` |

In practice, `DictReader` and `DictWriter` are preferred because they make your code clearer and more maintainable.

---

## Common CSV Pitfalls

- **Numbers are strings:** CSV values are always strings. Convert with `int()` or `float()` when needed.
- **Commas in data:** If a field contains a comma (e.g., `"New York, NY"`), surround it with quotes. The `csv` module handles this automatically.
- **Newlines:** Always use `newline=""` when writing CSV files.
- **Missing values:** Use `.get()` with DictReader rows to handle missing fields gracefully.

---

## Try It Yourself

1. Create a CSV file called `students.csv` with columns: `name`, `grade`, `subject`
2. Add 3-4 rows of data
3. Write a Python script that reads the CSV and prints each student's name and grade
4. Then write a new CSV with only the students who have grade A

---

## Summary

- **CSV** stores tabular data as plain text with commas separating values
- **`csv.reader`** / **`csv.DictReader`** read CSV files as lists or dictionaries
- **`csv.writer`** / **`csv.DictWriter`** write data to CSV files
- Always use `newline=""` when writing CSV files
- CSV values are strings — convert to numbers manually when needed
