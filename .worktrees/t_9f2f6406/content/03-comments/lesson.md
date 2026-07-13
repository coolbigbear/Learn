# Lesson 3: Comments

## Learning Objectives

- Write single-line comments with the `#` symbol
- Add comments on their own line
- Add comments at the end of a line of code
- Understand how comments help you and others read code

---

## What is a Comment?

A **comment** is a note you leave in your code for yourself or other programmers. Python ignores comments completely — they don't affect how your program runs.

Comments start with the `#` symbol:

```python
# This is a comment. Python won't run this line.
print("Hello")
```

Output:

```
Hello
```

The comment line is skipped. Only the `print()` line runs.

---

## Comments on Their Own Line

The most common way to use a comment is on its own line, above the code it explains:

```python
# Display a greeting to the user
print("Welcome to Python!")

# Calculate and show the result
print(3 + 4)
```

Output:

```
Welcome to Python!
7
```

Use complete sentences or short phrases that explain **why** the code does something, not just **what** it does.

---

## Inline Comments

You can also put a comment at the **end of a line of code**:

```python
print("Hello!")  # This greets the user
```

Everything after the `#` on that line is a comment. Everything before the `#` is code that runs normally.

Inline comments are useful for short notes about a specific line.

---

## Why Use Comments?

Comments make your code easier to understand. Here are the main reasons to use them:

**Explain your thinking:**
```python
# Convert Celsius to Fahrenheit using the formula
print((9 / 5) * 25 + 32)
```

**Leave reminders for yourself:**
```python
# TODO: Add error handling for invalid input
print("Processing...")
```

**Temporarily disable code:**
```python
# print("This won't run")
print("This will run")
```

By adding a `#` at the start of a line, you **comment out** that line — Python skips it. This is great for testing.

---

## What NOT to Comment

Don't write comments that just repeat what the code obviously does:

```python
# Bad comment — it just repeats the code
print("Hello")  # Print Hello

# Good comment — it explains the purpose
print("Hello")  # Greet the user when they log in
```

Write comments that add **value** — explain the "why", not the "what".

---

## Summary

- Comments start with `#` and are ignored by Python
- Put comments on their own line to explain the code below
- Put inline comments at the end of a line of code
- Use comments to explain your thinking, leave reminders, or temporarily disable code
- Don't state the obvious — add value with your comments

## What's Next

Now you know how to annotate your code with comments. Next up: **printing numbers** — how to display numbers without quotes.
