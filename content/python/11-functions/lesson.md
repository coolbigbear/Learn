# Lesson 11: Functions

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Define your own functions with `def`
> - Return values with `return`
> - Pass data into functions with parameters
> - Understand variable scope (local vs. global)
> - Document functions with docstrings

---

## What is a Function?

A **function** is a reusable block of code that performs a specific task. You've already used several — `print()`, `len()`, `type()` — but now you'll learn to create your own.

```python
def greet():
    print("Hello, welcome to Python!")
```

To run the function, you **call** it by name:

```python
greet()  # Output: Hello, welcome to Python!
```

### The `def` Keyword

- `def` tells Python you're defining a function
- Follow it with the function name and parentheses `()`
- End the line with a colon `:`
- Indent the function body (4 spaces)

---

## Parameters — Passing Data In

**Parameters** are variables that receive data when the function is called:

```python
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # Output: Hello, Alice!
greet("Bob")    # Output: Hello, Bob!
```

### Multiple Parameters

```python
def introduce(name, age):
    print(f"I'm {name} and I'm {age} years old.")

introduce("Alice", 25)  # Output: I'm Alice and I'm 25 years old.
```

### Default Parameter Values

You can provide default values that are used when the caller doesn't supply that argument:

```python
def greet(name="friend"):
    print(f"Hello, {name}!")

greet("Alice")   # Hello, Alice!
greet()          # Hello, friend!
```

---

## Return Values

A function can send data back to the caller with `return`:

```python
def add(a, b):
    result = a + b
    return result

total = add(5, 3)
print(total)  # 8
```

After `return`, the function stops immediately — any code after it won't run.

### Functions That Return vs. Functions That Print

This is a crucial distinction:

```python
# This function RETURNS a value
def double(n):
    return n * 2

result = double(5)   # result = 10
print(result)        # 10

# This function only PRINTS — can't use the result
def double_print(n):
    print(n * 2)

result = double_print(5)  # prints 10
print(result)             # None  (no return value)
```

**Rule of thumb:** If you want to _use_ the result later, use `return`. If you just want to display something, use `print`.

---

## Variable Scope

Variables defined inside a function are **local** — they only exist inside that function:

```python
def my_func():
    x = 10  # x is local to my_func
    print(x)

my_func()    # 10
# print(x)   # NameError! x doesn't exist here
```

Variables defined outside a function are **global**:

```python
y = 5  # global variable

def show_y():
    print(y)  # functions can read global variables

show_y()  # 5
```

But to **modify** a global variable inside a function, you need the `global` keyword (usually best to avoid this):

```python
counter = 0

def increment():
    global counter
    counter += 1

increment()
print(counter)  # 1
```

---

## Docstrings — Documenting Your Functions

A **docstring** is a multi-line string right after the `def` line that explains what the function does:

```python
def calculate_area(length, width):
    """Calculate the area of a rectangle.

    Args:
        length: The rectangle's length.
        width: The rectangle's width.

    Returns:
        The area as a float or int.
    """
    return length * width
```

Docstrings are accessible with `help()` or the `__doc__` attribute:

```python
help(calculate_area)
print(calculate_area.__doc__)
```

Good docstrings help other programmers (and future you) understand your functions.

---

## Putting It All Together

Here's a complete example:

```python
def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

temp_c = 25
temp_f = celsius_to_fahrenheit(temp_c)
print(f"{temp_c}°C is {temp_f}°F")
# Output: 25°C is 77.0°F
```

---

## Try It Yourself

1. Write a function `greet(name)` that prints "Hello, {name}!"
2. Write a function `add(a, b)` that **returns** the sum of two numbers.
3. Write a function `is_even(n)` that returns `True` if a number is even, `False` otherwise.
4. Write a function `convert_temp(celsius)` that converts Celsius to Fahrenheit and returns the result.

---

## Summary

- `def` defines a function — reusable, named code blocks
- Parameters let you pass data into functions
- `return` sends a value back to the caller
- Variables inside functions are local (scope matters)
- Docstrings document what a function does
