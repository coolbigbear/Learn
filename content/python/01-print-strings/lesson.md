# Lesson 1: Print Strings

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Use the `print()` function to display text
> - Create strings with double quotes `"..."` and single quotes `'...'`
> - Understand that print() puts each result on its own line

---

## Your First Program

Every programming journey starts with a tradition: making the computer say something. In Python, you do this with the `print()` function.

Type this into the editor and run it:

```python
print("Hello, World!")
```

When you run this, Python outputs:

```
Hello, World!
```

That's it — you just wrote your first Python program!

---

## How `print()` Works

`print()` is a **function** built into Python. A function is like a command that tells Python to do something.

The `print()` function takes whatever you put inside the parentheses and displays it on the screen.

Whatever you put in gets printed, and then Python starts a **new line** so the next `print()` appears below:

```python
print("First line")
print("Second line")
```

Output:

```
First line
Second line
```

Each `print()` adds a newline at the end automatically.

---

## What is a String?

The text `"Hello, World!"` is a **string**. A string is a piece of text wrapped in quotation marks.

The quotes tell Python: "This is text, not code."

```python
print("This is a string")
```

Without quotes, Python would try to interpret the words as code, which would cause an error.

---

## Double Quotes vs. Single Quotes

You can use either **double quotes** `"..."` or **single quotes** `'...'` to create a string:

```python
print("Hello with double quotes")
print('Hello with single quotes')
```

Both produce the same output:

```
Hello with double quotes
Hello with single quotes
```

Python treats them the same way. There's no difference — just pick one and be consistent.

**However**, you must use the **same** type of quote to open and close a string. Mixing them causes an error:

```python
print("Mismatched quotes')   # Error!
```

This is a **mismatched quote** error — the string starts with `"` but ends with `'`.

---

## Common Mistake: Forgetting Quotes

If you forget the quotes around text, Python thinks you're referring to a variable (which we'll learn about later) instead of a string:

```python
print(Hello)   # Error! Python thinks Hello is a variable name
```

Always wrap text in quotes when you want to print it as-is.

---

## Summary

- `print()` displays output on the screen
- Text you print must be wrapped in quotes — this is called a **string**
- Use either `"double quotes"` or `'single quotes'` — just make them match
- Each `print()` starts a new line automatically
- Forgetting quotes around text causes an error
