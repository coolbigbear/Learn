# Lesson 15: Modules and Packages

## Learning Objectives

- Import and use Python's built-in modules
- Create your own modules to organize code
- Understand packages and the `__init__.py` file
- Install third-party packages with `pip`
- Use `if __name__ == "__main__"` correctly

---

## What Are Modules?

As your programs grow, keeping everything in one file becomes messy. **Modules** let you split your code across multiple files. A module is simply a `.py` file that contains Python code — functions, classes, variables — that you can **import** and use in other files.

Think of modules as **toolboxes**. Instead of building every tool from scratch, you grab the toolbox you need.

---

## Importing Built-in Modules

Python comes with a huge **standard library** — modules for math, dates, file handling, web access, and much more. Let's explore a few:

### The `math` Module

```python
import math

print(math.pi)           # 3.141592653589793
print(math.sqrt(16))     # 4.0
print(math.floor(3.7))   # 3
print(math.ceil(3.2))    # 4
```

### The `random` Module

```python
import random

print(random.randint(1, 10))     # Random integer between 1 and 10
print(random.choice(["a", "b", "c"]))  # Random item from a list
print(random.shuffle([1, 2, 3, 4]))    # Shuffle a list in place
```

### The `datetime` Module

```python
import datetime

today = datetime.date.today()
now = datetime.datetime.now()
print(f"Today is {today}")
print(f"The time is {now.strftime('%H:%M')}")
```

---

## Different Ways to Import

### Import the whole module

```python
import math
print(math.sqrt(25))  # Must use math.sqrt
```

### Import specific items

```python
from math import sqrt, pi
print(sqrt(25))   # Just sqrt, no math. needed
print(pi)         # Just pi
```

### Import with an alias

```python
import numpy as np           # Common alias
import pandas as pd          # Very common!
from datetime import datetime as dt

now = dt.now()
```

### Import everything (use with caution!)

```python
from math import *  # Imports ALL names from math
print(sin(0))       # Works, but where did sin come from?
print(cos(0))
```

Using `*` can cause **name collisions** if two modules define the same function. It's better to be explicit.

---

## Creating Your Own Module

Making a module is simple: just write a `.py` file and import it.

**File: `greetings.py`**
```python
def say_hello(name):
    return f"Hello, {name}!"

def say_goodbye(name):
    return f"Goodbye, {name}!"

favorite_greeting = "Aloha"
```

**File: `main.py`** (in the same folder)
```python
import greetings

print(greetings.say_hello("Alice"))       # "Hello, Alice!"
print(greetings.favorite_greeting)        # "Aloha"
```

Or using `from`:
```python
from greetings import say_hello, say_goodbye

print(say_hello("Bob"))    # "Hello, Bob!"
print(say_goodbye("Bob"))  # "Goodbye, Bob!"
```

---

## The `if __name__ == "__main__"` Trick

When you import a module, Python runs **all the code** in that file. That's a problem if your module has test code or examples at the bottom:

**File: `calculator.py`**
```python
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# This runs when imported!
print("Testing: 2 + 3 =", add(2, 3))
```

If another file imports `calculator`, it'll print the test message. The fix:

```python
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

if __name__ == "__main__":
    # This only runs when you run calculator.py directly
    print("Testing: 2 + 3 =", add(2, 3))
```

`__name__` is `"__main__"` when a file is run directly, and the module's name when imported. This is how Python scripts double as importable modules.

---

## Packages: Organizing Multiple Modules

A **package** is a folder containing module files plus an `__init__.py` file (which can be empty). The `__init__.py` tells Python "this folder is a package."

```
my_package/
    __init__.py
    greetings.py
    calculator.py
```

```python
from my_package import greetings
from my_package.calculator import add

print(greetings.say_hello("Alice"))
print(add(2, 3))
```

---

## Installing Third-Party Packages with `pip`

While the standard library is useful, the real power of Python comes from the **community** — millions of packages you can install with `pip`.

```bash
pip install requests      # For making HTTP requests
pip install fastapi       # For building APIs
pip install pandas        # For data manipulation
pip install flask         # For web applications
```

Once installed, import them like any other module:

```python
import requests
response = requests.get("https://api.github.com")
print(response.status_code)
```

---

## Useful Standard Library Modules

| Module | What it's for |
|--------|-------------|
| `math` | Mathematical functions (sqrt, sin, pi) |
| `random` | Random numbers and choices |
| `datetime` | Working with dates and times |
| `json` | Reading and writing JSON data |
| `csv` | Reading and writing CSV files |
| `os` | Operating system interfaces (files, paths) |
| `pathlib` | Object-oriented file paths |
| `sys` | System-specific parameters |
| `collections` | Specialized data structures |
| `statistics` | Statistical functions (mean, median) |

---

## Try It Yourself

1. Import the `random` module and write a program that simulates rolling a six-sided die (prints a random number 1-6).
2. Create a module called `string_utils.py` with functions `reverse_string(s)` and `count_vowels(s)`. Then import and use it in a main script.
3. Use `if __name__ == "__main__"` to add test code to `string_utils.py` that only runs when the file is executed directly.

---

## Common Mistakes

- **Name collisions:** `from math import *` and `from statistics import *` both define `mean` — one overwrites the other.
- **Circular imports:** Module A imports Module B, and Module B imports Module A. This creates an error.
- **Forgetting `__init__.py`:** In Python 3.3+, packages don't strictly need it, but it's good practice for clarity.
- **Not separating test code:** Always use `if __name__ == "__main__"` to protect importable code.

---

## Summary

- A **module** is a `.py` file; a **package** is a folder of modules
- `import` brings in modules; `from ... import ...` brings in specific items
- The **standard library** has modules for almost everything
- Create your own modules by writing `.py` files with functions and classes
- `if __name__ == "__main__"` prevents test code from running on import
- `pip install` adds third-party packages to your Python environment

## What's Next

Now that you can use modules and packages, let's apply that to **data processing** (Lesson 16) — reading CSV files, working with JSON, and making your first API calls.