# Lesson 6: Strings

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Create strings with single, double, and triple quotes
> - Combine strings with concatenation
> - Embed variables in strings with f-strings
> - Use string methods like `.upper()`, `.lower()`, and `len()`

---

## What is a String?

A **string** is a sequence of characters — letters, numbers, spaces, punctuation. You create one by wrapping text in quotes:

```python
greeting = "Hello"
name = 'Alice'
empty = ""
```

Both single quotes `'...'` and double quotes `"..."` work. Choose whichever lets you avoid escaping; see below.

### Quotes Inside Strings

What if your string contains a quote character? You have options:

```python
# Use the other quote type
text1 = "It's a nice day"
text2 = 'She said "Hello"'

# Or escape with backslash
text3 = 'It\'s a nice day'
```

### Multi-line Strings with Triple Quotes

Use three quotes `"""` or `'''` for strings that span multiple lines:

```python
poem = """Roses are red,
Violets are blue,
Python is fun,
And so are you!"""
print(poem)
```

---

## String Concatenation

**Concatenation** means joining strings together with the `+` operator:

```python
first = "Alice"
last = "Smith"
full = first + " " + last
print(full)  # Alice Smith
```

You can also use `*` to repeat a string:

```python
print("Ha" * 3)  # HaHaHa
```

---

## f-Strings (Formatted Strings)

f-strings are the cleanest way to embed variables in strings. Put an `f` before the opening quote and use `{variable}` inside:

```python
name = "Alice"
age = 25
print(f"{name} is {age} years old.")
# Output: Alice is 25 years old.
```

You can even put expressions inside the curly braces:

```python
print(f"Next year {name} will be {age + 1}.")
# Output: Next year Alice will be 26.
```

f-strings are preferred over concatenation for readability.

---

## Common String Methods

Strings come with built-in **methods** — functions that belong to the string object. Call them with dot notation:

### `.upper()` and `.lower()`

```python
message = "Hello, World!"
print(message.upper())  # HELLO, WORLD!
print(message.lower())  # hello, world!
```

### `len()`

`len()` is a built-in function (not a method) that returns the length:

```python
print(len("Python"))  # 6
print(len(""))        # 0
```

### `.strip()`

Removes whitespace from the start and end:

```python
text = "   messy   "
print(text.strip())  # "messy"
```

### `.replace()`

Replaces all occurrences of a substring:

```python
text = "I like cats"
print(text.replace("cats", "dogs"))  # I like dogs
```

### `.count()`

Counts how many times a substring appears:

```python
text = "hello hello hello"
print(text.count("hello"))  # 3
```

---

## Checking What's in a String

Use the `in` operator to check if a substring exists:

```python
sentence = "The quick brown fox"
print("quick" in sentence)   # True
print("slow" in sentence)    # False
```

---

## Try It Yourself

1. Create a string with your full name and print its length.
2. Use an f-string to print "My name is X and I am Y years old" with variables.
3. Take a sentence, convert it to uppercase, and print it.
4. Use `.replace()` to swap two words in a sentence.

---

## Summary

- Strings store text — use `'...'` or `"..."` quotes
- Concatenate with `+`, embed variables with f-strings
- Methods like `.upper()`, `.lower()`, `.strip()` transform strings
- `len()` gives the character count
- The `in` operator checks for substrings
