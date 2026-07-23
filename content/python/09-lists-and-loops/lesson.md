# Lesson 9: Lists and Loops

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Create and modify lists
> - Access individual elements by index
> - Iterate over lists with `for` loops
> - Use `range()` to repeat a set number of times
> - Use `.append()` to grow a list

---

## What is a List?

A **list** is an ordered collection of items. You create one with square brackets `[]`, separating items with commas:

```python
colors = ["red", "green", "blue"]
numbers = [1, 2, 3, 4, 5]
mixed = ["hello", 42, 3.14, True]
```

Lists can hold any type — and different types can live in the same list.

---

## Accessing Elements by Index

Each item in a list has an **index** — its position number, starting from **0**:

```python
colors = ["red", "green", "blue"]
print(colors[0])  # red
print(colors[1])  # green
print(colors[2])  # blue
print(colors[-1]) # blue  (negative index = from the end)
print(colors[-2]) # green
```

### List Length

Use `len()` to get how many items are in a list:

```python
print(len(colors))  # 3
```

### Slicing

Get a portion of a list with `[start:end]`:

```python
nums = [10, 20, 30, 40, 50]
print(nums[1:4])   # [20, 30, 40]
print(nums[:3])    # [10, 20, 30]
print(nums[2:])    # [30, 40, 50]
```

The slice includes the start index but **excludes** the end index.

---

## Modifying Lists

Lists are **mutable** — you can change them:

```python
colors = ["red", "green", "blue"]

# Change an element
colors[1] = "yellow"
print(colors)  # ["red", "yellow", "blue"]

# Add to the end
colors.append("purple")
print(colors)  # ["red", "yellow", "blue", "purple"]

# Remove an element
colors.remove("red")
print(colors)  # ["yellow", "blue", "purple"]

# Insert at a specific position
colors.insert(1, "orange")
print(colors)  # ["yellow", "orange", "blue", "purple"]
```

---

## The `for` Loop

A `for` loop lets you do something with **each item** in a list:

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(f"I like {fruit}")
```

Output:

```
I like apple
I like banana
I like cherry
```

The variable after `for` (here `fruit`) takes the value of each list item in turn. The indented block runs once per item.

---

## `range()` — Counting Loops

`range()` generates a sequence of numbers. Use it with `for` to repeat something a certain number of times:

```python
# range(5) gives 0, 1, 2, 3, 4
for i in range(5):
    print(f"Count: {i}")
```

Output:

```
Count: 0
Count: 1
Count: 2
Count: 3
Count: 4
```

### `range(start, stop, step)`

```python
for i in range(2, 10, 2):
    print(i)  # 2, 4, 6, 8
```

- `start`: where to begin (default 0)
- `stop`: where to end (exclusive — doesn't include this number)
- `step`: how much to skip (default 1)

---

## Common Loop Patterns

### Summing numbers

```python
numbers = [3, 8, 2, 10, 5]
total = 0

for n in numbers:
    total += n  # same as: total = total + n

print(total)  # 28
```

### Building a new list

```python
numbers = [1, 2, 3, 4, 5]
squares = []

for n in numbers:
    squares.append(n ** 2)

print(squares)  # [1, 4, 9, 16, 25]
```

### Looping with index

Use `enumerate()` to get both the index and the value:

```python
colors = ["red", "green", "blue"]

for i, color in enumerate(colors):
    print(f"{i}: {color}")

# Output:
# 0: red
# 1: green
# 2: blue
```

---

## Try It Yourself

1. Create a list of 5 favorite movies and print each one using a `for` loop.
2. Write a loop that sums all numbers from 1 to 100 (use `range()`).
3. Given a list of numbers, create a new list containing only the even numbers.
4. Build a grocery list: start with an empty list, use `.append()` to add 4 items, then print each item with its index.

---

## Summary

- Lists store ordered collections using `[]`
- Access items by index starting at 0; negative indexes count from the end
- `.append()` adds items, `.remove()` removes them
- `for` loops iterate over each item in a list
- `range()` generates sequences of numbers for counting loops
