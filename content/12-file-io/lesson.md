# Lesson 12: File Input / Output

## Learning Objectives

- Open and read text files with Python
- Write and append data to files
- Use `with` statements (context managers) for safe file handling
- Understand file modes: read, write, append
- Handle different file encodings

---

## Why Files Matter

So far, everything you've coded has existed only in memory. When the program ends, the data disappears. Files let you **persist data** — save it to disk so you can read it back later, share it, or process it in another program.

Think of a file like a notebook. You can:
- **Read** it (open and look at what's written)
- **Write** to it (erase and start fresh)
- **Append** to it (add new pages at the end)

---

## Opening a File: The `open()` Function

To work with a file in Python, you first **open** it using `open()`. You need to specify the filename and the **mode** (what you want to do with it).

```python
file = open("hello.txt", "r")   # "r" = read mode
content = file.read()            # Read everything
print(content)
file.close()                     # Always close when done!
```

### File Modes

| Mode | Name | What it does |
|------|------|-------------|
| `"r"` | Read | Opens file for reading. Error if file doesn't exist. |
| `"w"` | Write | Opens file for writing. Creates new file or **overwrites** existing. |
| `"a"` | Append | Opens file for adding content at the end. Creates if missing. |
| `"x"` | Exclusive | Creates a new file. Error if it already exists. |
| `"r+"` | Read+Write | Opens for both reading and writing. |

Add `"b"` for binary mode (images, audio): `"rb"`, `"wb"`.

### The Danger of Forgetting `.close()`

If your program crashes after `open()` but before `.close()`, the file might get corrupted or waste system resources. That's why we use the **`with` statement** instead.

---

## The `with` Statement — Safe File Handling

The `with` statement automatically closes the file, even if an error happens:

```python
with open("hello.txt", "r") as file:
    content = file.read()
    print(content)
# File is automatically closed here — no file.close() needed!
```

This is the **preferred way** to work with files in Python. Always use `with` unless you have a specific reason not to.

---

## Reading Files

### `read()` — Read Everything

```python
with open("story.txt", "r") as f:
    whole_thing = f.read()
    print(whole_thing)
```

### `readline()` — Read One Line at a Time

```python
with open("story.txt", "r") as f:
    line1 = f.readline()  # "Once upon a time...\n"
    line2 = f.readline()  # "There was a Python...\n"
```

Each call to `readline()` moves to the next line.

### `readlines()` — Read All Lines Into a List

```python
with open("story.txt", "r") as f:
    lines = f.readlines()  # ["Once upon a time...\n", "There was a Python...\n"]
    print(lines[0])        # First line
```

### Looping Over a File Line by Line

The most memory-efficient way to read a file:

```python
with open("story.txt", "r") as f:
    for line in f:
        print(line.strip())  # .strip() removes the trailing newline
```

This works because file objects are **iterable** — they yield one line at a time.

---

## Writing Files

### `write()` — Write Text

```python
with open("output.txt", "w") as f:
    f.write("Hello, file!\n")
    f.write("This is line two.\n")
```

**Important:** `"w"` mode **overwrites** the entire file! If `output.txt` already had content, it's gone.

### `writelines()` — Write a List of Strings

```python
lines = ["Line A\n", "Line B\n", "Line C\n"]
with open("output.txt", "w") as f:
    f.writelines(lines)
```

Note: `writelines()` does NOT add newlines for you — your strings must include `\n`.

---

## Appending to Files

Use `"a"` mode to add content without destroying what's already there:

```python
with open("log.txt", "a") as f:
    f.write("2026-07-01: User logged in\n")
```

Each run adds a new line at the end. The old content stays.

---

## Working With Paths

You can use relative or absolute paths. On different operating systems, path separators differ (`\` on Windows, `/` on Mac/Linux). The `pathlib` module handles this cross-platform:

```python
from pathlib import Path

path = Path("data") / "notes.txt"   # Automatically uses correct separator
with open(path, "r") as f:
    print(f.read())
```

Or even simpler with `Path.read_text()` and `Path.write_text()`:

```python
from pathlib import Path

path = Path("data/notes.txt")

# Read
content = path.read_text()
print(content)

# Write
path.write_text("New content here")
```

---

## Checking If a File Exists

Before opening a file for reading, it's wise to check if it exists:

```python
from pathlib import Path

path = Path("data.txt")
if path.exists():
    with open(path, "r") as f:
        print(f.read())
else:
    print("File not found!")
```

---

## Try It Yourself

1. Write a program that saves a list of your favorite foods to a file (one per line).
2. Write a program that reads that file back and prints each line with a number.
3. Write a program that appends a new food to the file without deleting existing content.

---

## Common Mistakes

- **Forgetting the mode:** `open("file.txt")` defaults to `"r"`, but being explicit is clearer.
- **Writing in `"r"` mode:** You'll get an `io.UnsupportedOperation` error.
- **Not stripping newlines:** `line.strip()` removes the `\n` that `readline()` includes.
- **Opening a nonexistent file in `"r"` mode:** Raises `FileNotFoundError`.

---

## Summary

- `open(filename, mode)` returns a file object
- Always use `with open(...) as f:` to auto-close files
- Read with `.read()`, `.readline()`, `.readlines()`, or loop over the file
- Write with `.write()` or `.writelines()`
- Append with `"a"` mode to preserve existing content
- `pathlib.Path` provides a cleaner, cross-platform way to handle file paths

## What's Next

Now that you can read and write files, let's talk about **error handling** (Lesson 13) — what happens when things go wrong and how to handle them gracefully.