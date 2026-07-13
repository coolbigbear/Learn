# Lesson 5: Variables and Data Types

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Store data in variables
> - Follow Python's variable naming rules
> - Work with integers, floats, strings, and booleans
> - Check the type of any value with `type()`

---

## What is a Variable?

A **variable** is a named container that holds a value. Think of it like a labeled box — you put something in the box, and the label tells you what's inside.

```python
name = "Alice"
age = 25
height = 1.68
is_student = True
```

- `name` holds the string `"Alice"`
- `age` holds the integer `25`
- `height` holds the float `1.68`
- `is_student` holds the boolean `True`

The single equals sign `=` is the **assignment operator**. It takes the value on the right and stores it in the variable name on the left.

### Using Variables

Once a variable is assigned, you can use it anywhere you'd use the actual value:

```python
name = "Alice"
print(name)       # Output: Alice
print("Hi,", name)  # Output: Hi, Alice
```

You can even use a variable to calculate a new value:

```python
age = 25
next_year = age + 1
print(next_year)  # Output: 26
```

---

## Variable Naming Rules

Python has a few fixed rules and some strong conventions:

### Rules (Python will error if you break these)

| Rule | Bad example | Good example |
|------|-------------|--------------|
| Start with a letter or underscore | `2cool = 5` | `cool2 = 5` |
| Only letters, numbers, underscores | `my-var = 1` | `my_var = 1` |
| No Python keywords | `if = 10` | `if_value = 10` |

### Conventions (you _should_ follow these)

- **Use snake_case:** `my_variable`, not `myVariable` or `MyVariable`
- **Use descriptive names:** `temperature` not `t`, `user_age` not `ua`
- **Use UPPERCASE for constants:** `PI = 3.14159`

---

## Basic Data Types

Python has four fundamental data types you'll use constantly:

### Integer (`int`)

Whole numbers, positive or negative:

```python
count = 10
temperature = -5
large_number = 1_000_000  # Underscores make large numbers readable
```

### Float (`float`)

Numbers with decimal points:

```python
price = 19.99
pi = 3.14159
scientific = 1.5e10  # 1.5 × 10^10
```

### String (`str`)

Text wrapped in quotes:

```python
greeting = "Hello"
name = 'Alice'
multiline = """This spans
multiple lines"""
```

Strings can use single quotes `'...'` or double quotes `"..."` — just be consistent.

### Boolean (`bool`)

Only two possible values: `True` or `False`:

```python
is_raining = True
is_sunny = False
```

Booleans are essential for decision-making, which we'll cover in Lesson 8.

---

## Checking Types with `type()`

Use the `type()` function to see what type a value is:

```python
print(type(42))       # <class 'int'>
print(type(3.14))     # <class 'float'>
print(type("Hello"))  # <class 'str'>
print(type(True))     # <class 'bool'>
```

This is very useful for debugging — if something behaves unexpectedly, check its type!

---

## Reassigning Variables

Variables can change value over time:

```python
temperature = 20
print(temperature)  # 20

temperature = 25
print(temperature)  # 25

temperature = temperature + 5
print(temperature)  # 30
```

The old value is replaced. You can also use the current value to compute a new one.

---

## Try It Yourself

1. Create a variable called `city` storing your favorite city, and print it.
2. Create two variables `a` and `b` with different numbers. Swap their values so `a` gets `b`'s value and `b` gets `a`'s old value.
3. Use `type()` to print the type of each variable you created.

---

## Summary

- Variables store values using the `=` assignment operator
- Follow naming rules (letters, underscores, numbers — no keywords)
- Python has four basic types: `int`, `float`, `str`, `bool`
- Use `type()` to check what type something is
- Variables can be reassigned to new values
