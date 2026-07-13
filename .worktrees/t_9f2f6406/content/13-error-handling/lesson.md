# Lesson 13: Error Handling and Exceptions

## Learning Objectives

- Understand what exceptions are and why they occur
- Catch and handle exceptions with `try` / `except`
- Use `else` and `finally` for fine-grained control
- Raise your own exceptions with `raise`
- Handle multiple exception types

---

## What Are Exceptions?

When Python runs into a problem, it doesn't just crash silently — it raises an **exception** (also called an error). You've probably seen some already:

```python
print(1 / 0)        # ZeroDivisionError: division by zero
int("hello")        # ValueError: invalid literal for int()
open("nope.txt")    # FileNotFoundError: No such file or directory
```

Each of these is an **exception** — Python's way of saying "I don't know how to handle this." When an exception isn't handled, the program stops and shows an **error traceback**.

But you don't have to let your program crash! You can **catch** exceptions and handle them gracefully.

---

## The `try` / `except` Block

The simplest way to handle an exception is with `try` and `except`:

```python
try:
    risky_code = int(input("Enter a number: "))
except:
    print("That wasn't a number!")
```

If the code inside `try` raises an exception, Python jumps to the `except` block instead of crashing.

### Catching Specific Exceptions

It's better to catch only the exceptions you expect. This way, real bugs still show up:

```python
try:
    number = int(input("Enter a number: "))
    result = 10 / number
    print(f"10 / {number} = {result}")
except ValueError:
    print("You didn't enter a valid number!")
except ZeroDivisionError:
    print("You can't divide by zero!")
```

Now each error has its own handler. A `ValueError` (wrong type) and a `ZeroDivisionError` are handled differently.

### Getting the Error Message

You can capture the exception object to see what went wrong:

```python
try:
    age = int(input("Enter your age: "))
except ValueError as e:
    print(f"Error: {e}")  # e holds the error message
```

---

## The `else` Block

You can add an `else` block that runs **only if no exception occurred**:

```python
try:
    age = int(input("Enter your age: "))
except ValueError:
    print("That wasn't a number!")
else:
    print(f"You are {age} years old.")  # Only runs if no error
```

---

## The `finally` Block

The `finally` block runs **no matter what** — whether there's an exception or not. It's great for cleanup (closing files, releasing resources):

```python
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    file.close()  # Always runs — even if the file didn't exist
```

Actually, we learned in Lesson 12 that `with` handles this automatically. But `finally` is there when you need custom cleanup.

---

## Complete Error Handling Structure

Here's the full pattern, from most specific to least:

```python
try:
    # Code that might fail
    result = risky_operation()
except ValueError:
    # Handle specific error
    print("Value problem")
except (TypeError, ZeroDivisionError) as e:
    # Handle multiple error types at once
    print(f"Type or math error: {e}")
except Exception as e:
    # Catch ANY exception (use sparingly!)
    print(f"Unexpected error: {e}")
else:
    # No exception occurred
    print("Success!")
finally:
    # Always runs
    print("Cleanup done")
```

**Important:** Catching `Exception` (or worse, bare `except`) is a last resort. It hides bugs. Catch specific exceptions when you can.

---

## Raising Your Own Exceptions

Sometimes you want to signal that something is wrong in your own code. Use `raise`:

```python
def set_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative!")
    if age > 150:
        raise ValueError("Age is unrealistic!")
    print(f"Age set to {age}")

set_age(-5)  # Raises ValueError
```

You can raise built-in exceptions or create your own custom ones by inheriting from `Exception`:

```python
class NegativeBalanceError(Exception):
    """Raised when a bank account goes negative."""
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise NegativeBalanceError("Insufficient funds!")
    return balance - amount
```

---

## Common Built-in Exceptions

| Exception | When it occurs |
|-----------|---------------|
| `ValueError` | Wrong value type (e.g., `int("hello")`) |
| `TypeError` | Wrong operation on a type (e.g., `"hi" + 5`) |
| `ZeroDivisionError` | Division by zero |
| `FileNotFoundError` | File doesn't exist |
| `IndexError` | List index out of range |
| `KeyError` | Dictionary key not found |
| `ImportError` | Module not found |
| `AttributeError` | Object has no such attribute |

---

## Try It Yourself

1. Write a program that asks for a number and handles both `ValueError` (non-number input) and `ZeroDivisionError` (dividing by zero).
2. Create a function `divide(a, b)` that raises a `ValueError` if `b` is zero, with a custom message.
3. Write a program that reads a file but gracefully handles the case where the file doesn't exist.

---

## Common Mistakes

- **Catching too broadly:** `except:` catches everything, including `KeyboardInterrupt` (Ctrl+C). Use `except Exception:` or specific types.
- **Empty except blocks:** `except: pass` silently swallows errors. At least log them!
- **Not ordering exceptions properly:** Put more specific exceptions before more general ones.
- **Raising without a message:** `raise ValueError` is OK, but `raise ValueError("explanation")` is much more helpful.

---

## Summary

- Exceptions are Python's way of reporting errors
- `try` / `except` catches and handles exceptions gracefully
- `else` runs when no exception occurs; `finally` always runs
- Catch specific exceptions instead of using bare `except:`
- `raise` lets you signal errors in your own code
- Custom exception classes make error handling clearer

## What's Next

Now that you can handle errors gracefully, let's shift gears to **Object-Oriented Programming (OOP)** (Lesson 14) — a powerful way to organize your code using classes and objects.