# Lesson 2: Print Multiple Items

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Print multiple items in a single `print()` statement
> - Use commas to separate items
> - Understand how Python adds spaces between items
> - Combine strings and numbers in one print statement

---

## Printing Multiple Items

The `print()` function can take more than one item at a time. Just separate them with **commas**:

```python
print("Hello", "World")
```

Output:

```
Hello World
```

Python prints each item one after another, with a **space** between them.

---

## How Many Items Can You Print?

You can put as many items as you want inside a single `print()`:

```python
print("one", "two", "three", "four", "five")
```

Output:

```
one two three four five
```

Each comma adds another item. Python spaces them out automatically.

---

## Mixing Different Items

You can mix text (strings) and numbers in the same `print()`:

```python
print("I am", 25, "years old")
```

Output:

```
I am 25 years old
```

The space is added between each item automatically — you don't need to add spaces manually.

---

## The Space Between Items

Python automatically inserts a space between each item you pass to `print()`. This is the **default separator**.

```python
print("a", "b", "c")
```

Output:

```
a b c
```

Notice the spaces between `a`, `b`, and `c`. You didn't have to type them — Python handles it.

If you want items to run together without spaces, you'd need a different approach (we'll cover that in a later lesson). For now, enjoy the automatic spacing!

---

## Using Single and Double Quotes Together

When printing multiple items, you can use single quotes for some and double quotes for others:

```python
print("Hello", 'there', "world")
```

Output:

```
Hello there world
```

Python doesn't care which quote style you use for each item — they all work the same way.

---

## Summary

- Separate multiple items with commas inside `print()`
- Python adds a space between each item automatically
- You can mix strings and numbers in the same print statement
- Each item can use either single or double quotes independently
