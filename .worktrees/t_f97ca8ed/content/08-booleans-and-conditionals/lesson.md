# Lesson 8: Booleans and Conditionals

## Learning Objectives

- Use comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Write `if`/`elif`/`else` statements to make decisions
- Combine conditions with `and`, `or`, and `not`
- Understand truthy and falsy values

---

## What is a Boolean?

A **boolean** has only two possible values: `True` or `False`. They represent yes/no questions in your code.

```python
is_sunny = True
is_rainy = False
```

But usually, booleans come from **comparisons** — asking Python "is this true?"

---

## Comparison Operators

These compare two values and return `True` or `False`:

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `==` | Equal to | `5 == 5` | `True` |
| `!=` | Not equal to | `5 != 3` | `True` |
| `<` | Less than | `3 < 5` | `True` |
| `>` | Greater than | `3 > 5` | `False` |
| `<=` | Less than or equal | `5 <= 5` | `True` |
| `>=` | Greater than or equal | `5 >= 6` | `False` |

**Important:** `==` (two equals) checks equality. `=` (one equals) assigns a value.

```python
print(10 == 10)  # True
print(10 == 5)   # False
print("cat" == "dog")  # False
print(7 != 3)    # True
print(7 < 10)    # True
print(7 > 10)    # False
```

---

## The `if` Statement

The `if` statement lets you run code **only when a condition is true**:

```python
age = 18

if age >= 18:
    print("You can vote!")
```

Key syntax points:
- The condition ends with a colon `:`
- The code to run is **indented** (4 spaces by convention)
- Python runs the indented block only if the condition is `True`

### `if` / `else`

Add `else` to run code when the condition is false:

```python
age = 16

if age >= 18:
    print("You can vote!")
else:
    print("Too young to vote.")
```

### `if` / `elif` / `else`

Use `elif` (short for "else if") for multiple conditions:

```python
score = 85

if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
else:
    print("Grade: F")
```

Python checks conditions **top to bottom**. The first `True` one wins, and the rest are skipped.

---

## Logical Operators: `and`, `or`, `not`

Combine multiple conditions with logical operators.

### `and` — both must be True

```python
age = 25
has_license = True

if age >= 18 and has_license:
    print("You can drive!")
```

### `or` — at least one must be True

```python
is_weekend = True
is_holiday = False

if is_weekend or is_holiday:
    print("No work today!")
```

### `not` — flips True to False and vice versa

```python
is_raining = False

if not is_raining:
    print("Let's go outside!")
```

---

## Truthy and Falsy Values

In Python, some values are considered "truthy" (act like `True`) or "falsy" (act like `False`) in conditions:

| Falsy values | Truthy values |
|--------------|---------------|
| `False` | `True` |
| `0`, `0.0` | Any non-zero number |
| `""` (empty string) | Any non-empty string |
| `None` | Any value that's not falsy |

```python
name = ""

if name:
    print(f"Hello, {name}!")
else:
    print("No name entered.")  # This runs because "" is falsy
```

---

## Try It Yourself

1. Write code that checks if a number is positive, negative, or zero and prints the result.
2. Ask the user's age with `input()` and check if they're old enough to drive (age >= 16).
3. Check if a year is a leap year (divisible by 400, or divisible by 4 but not by 100).
4. Write a login check: if username is "admin" AND password is "secret", print "Welcome"; otherwise print "Access denied".

---

## Summary

- Comparison operators `==`, `!=`, `<`, `>`, `<=`, `>=` return booleans
- `if`/`elif`/`else` lets your code make decisions
- `and`, `or`, `not` combine or flip conditions
- Empty and zero values are "falsy" — they act like `False` in conditions

## What's Next

Now that you can make decisions, let's learn about **lists and loops** — working with collections of data and repeating actions (Lesson 9).