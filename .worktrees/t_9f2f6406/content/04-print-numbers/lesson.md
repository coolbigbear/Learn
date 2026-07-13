# Lesson 4: Print Numbers

## Learning Objectives

- Print numbers directly without quotes
- Print whole numbers (integers) and decimal numbers (floats)
- Print multiple numbers in one statement
- Understand that numbers are not strings — no quotes needed

---

## Printing Numbers

Unlike text, numbers in Python don't need quotes. You can put them directly inside `print()`:

```python
print(42)
```

Output:

```
42
```

No quotes needed! The number `42` is just typed as-is.

---

## Why No Quotes for Numbers?

When you put quotes around a number, Python treats it as **text** (a string). Without quotes, Python treats it as an **actual number** you can do math with.

For now, just remember:
- **Text** needs quotes: `print("Hello")`
- **Numbers** don't need quotes: `print(42)`

But you can still put a number in quotes if you want it displayed as text — it will look the same on the screen. The difference matters when we start doing calculations (coming in a later lesson).

---

## Whole Numbers (Integers)

Whole numbers — positive, negative, or zero — are called **integers** in Python:

```python
print(7)
print(-3)
print(0)
print(1000000)
```

Output:

```
7
-3
0
1000000
```

No commas in large numbers. Just write the digits.

---

## Decimal Numbers (Floats)

Numbers with a decimal point are called **floats** in Python:

```python
print(3.14)
print(0.5)
print(-2.75)
```

Output:

```
3.14
0.5
-2.75
```

Use a dot `.` as the decimal separator — not a comma.

---

## Printing Multiple Numbers

You can print multiple numbers in one `print()`, separated by commas — just like with strings:

```python
print(5, 10, 15)
```

Output:

```
5 10 15
```

Python adds spaces between them automatically.

You can also mix numbers and strings:

```python
print("The answer is", 42)
```

Output:

```
The answer is 42
```

---

## Summary

- Numbers don't need quotes inside `print()`
- Whole numbers are called **integers** (e.g., `42`, `-7`, `0`)
- Decimal numbers are called **floats** (e.g., `3.14`, `-0.5`)
- Print multiple numbers with commas to get spaces between them
- You can mix strings and numbers in the same `print()`

## What's Next

Now you can print both text and numbers! Up next: **variables** — storing values in named containers so you can reuse them.