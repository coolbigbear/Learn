# Lesson 7: Numbers and Math

## Learning Objectives

- Use Python's arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Understand the difference between integers and floats
- Convert between types with `int()` and `float()`
- Handle common math pitfalls

---

## Python as a Calculator

Python can do arithmetic right in a `print()` call:

```python
print(5 + 3)    # 8
print(10 - 4)   # 6
print(6 * 7)    # 42
print(20 / 5)   # 4.0
```

Wait — `20 / 5` gave `4.0` not `4`! That's because division always returns a **float** (a number with a decimal), even when the result is a whole number.

---

## Printing Expressions

You can put calculations directly inside `print()` — Python evaluates them first, then prints the result:

```python
print(2 + 2)
```

Output:

```
4
```

Python calculated `2 + 2` to get `4`, then printed it. This works with any arithmetic expression:

```python
print(10 - 3)
print(4 * 5)
print(20 / 4)
```

Output:

```
7
20
5.0
```

You can even combine multiple expressions with text:

```python
print("Two plus two is", 2 + 2)
```

Output:

```
Two plus two is 4
```

This is a great way to display calculation results without storing them in variables first.

---

## Arithmetic Operators

| Operator | Name | Example | Result |
|----------|------|---------|--------|
| `+` | Addition | `10 + 3` | `13` |
| `-` | Subtraction | `10 - 3` | `7` |
| `*` | Multiplication | `10 * 3` | `30` |
| `/` | Division | `10 / 3` | `3.333...` |
| `//` | Floor Division | `10 // 3` | `3` |
| `%` | Modulo (remainder) | `10 % 3` | `1` |
| `**` | Exponentiation | `10 ** 3` | `1000` |

Let's look at the operators that might be new:

### Floor Division `//`

Floor division divides and rounds **down** to the nearest integer:

```python
print(10 // 3)   # 3
print(20 // 6)   # 3
print(-10 // 3)  # -4  (rounds DOWN, not toward zero)
```

### Modulo `%`

Modulo gives the **remainder** of a division:

```python
print(10 % 3)    # 1  (10 ÷ 3 = 3 remainder 1)
print(20 % 5)    # 0
print(7 % 2)     # 1  (odd numbers have remainder 1)
```

Modulo is great for checking if a number is even or odd (it's even if `number % 2 == 0`).

### Exponentiation `**`

```python
print(2 ** 3)    # 8   (2 × 2 × 2)
print(5 ** 2)    # 25  (5 squared)
print(9 ** 0.5)  # 3.0 (square root via fractional exponent)
```

---

## Operator Precedence

Python follows the same order of operations you learned in math class — PEMDAS:

1. **P**arentheses `()`
2. **E**xponentiation `**`
3. **M**ultiplication `*` and **D**ivision `/` (left to right)
4. **A**ddition `+` and **S**ubtraction `-` (left to right)

```python
print(2 + 3 * 4)      # 14  (3*4 first, then +2)
print((2 + 3) * 4)    # 20  (parentheses first)
print(10 - 2 + 3)     # 11  (left to right)
```

When in doubt, use parentheses to make your intention clear.

---

## Integers vs. Floats

| Type | Example | Notes |
|------|---------|-------|
| `int` | `5`, `-42`, `1_000_000` | Whole numbers only |
| `float` | `3.14`, `-0.5`, `1.0` | Numbers with decimals |

Mixing an `int` with a `float` in an operation gives a `float`:

```python
print(3 + 4.0)    # 7.0 (float)
print(10 / 5)     # 2.0 (division always gives float)
```

### Type Conversion

Use `int()` and `float()` to convert between types:

```python
# String to number
print(int("42"))       # 42
print(float("3.14"))   # 3.14

# Float to int (truncates, doesn't round)
print(int(3.99))       # 3

# Int to float
print(float(7))        # 7.0
```

Be careful — converting a string like `"hello"` to an int will crash:

```python
int("hello")  # ValueError!
```

---

## Useful Patterns

### Checking Even/Odd

```python
number = 7
if number % 2 == 0:
    print("Even")
else:
    print("Odd")
```

### Calculating Remainders

```python
minutes = 145
hours = minutes // 60    # 2
remaining = minutes % 60 # 25
print(f"{hours}h {remaining}m")  # 2h 25m
```

---

## Try It Yourself

1. Calculate the area of a rectangle with width 5.5 and height 3.2.
2. Use `%` to check if a number is even or odd and print the result.
3. Convert the string `"123"` to an integer, add 77 to it, and print the result.

---

## Summary

- Python supports standard math operators plus `//` (floor division), `%` (modulo), and `**` (exponentiation)
- Division `/` always returns a `float`
- Parentheses control order of operations
- Use `int()` and `float()` to convert between types

## What's Next

Now that you can calculate, let's learn about **booleans and conditionals** — making decisions in your code (Lesson 8).