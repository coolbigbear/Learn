# Lesson 14: Object-Oriented Programming (OOP)

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Understand the difference between a class and an object
> - Define your own classes with `class`
> - Create instance attributes and methods
> - Use `__init__` to initialize objects
> - Understand basic inheritance

---

## Why OOP?

So far, you've used Python's built-in types — strings, lists, dictionaries, etc. But what if you want to represent something more complex, like a **student**, a **bank account**, or a **video game character**?

Object-Oriented Programming lets you create your own custom types that bundle together **data** (attributes) and **behavior** (methods). Think of a class as a **blueprint** and an object as the **actual thing** built from that blueprint.

---

## Classes and Objects

A **class** is a template. An **object** (or instance) is a concrete thing made from that template.

```python
# Define a class (blueprint)
class Dog:
    pass  # Empty for now

# Create objects (actual dogs)
my_dog = Dog()
your_dog = Dog()

print(my_dog)   # <__main__.Dog object at 0x...>
print(type(my_dog))  # <class '__main__.Dog'>
```

Both `my_dog` and `your_dog` are **instances** of the `Dog` class. They're separate — changing one doesn't affect the other.

---

## The `__init__` Method

The `__init__` method (short for "initialize") is called automatically when you create a new object. It's where you set up the initial state:

```python
class Dog:
    def __init__(self, name, breed):
        self.name = name   # Instance attribute
        self.breed = breed # Instance attribute

# Each call to Dog() creates a new instance
my_dog = Dog("Buddy", "Golden Retriever")
your_dog = Dog("Luna", "Husky")

print(my_dog.name)   # "Buddy"
print(your_dog.breed)  # "Husky"
```

The `self` parameter refers to the **current instance**. When you call `Dog("Buddy", ...)`, Python automatically passes the new object as `self`.

---

## Adding Methods

**Methods** are just functions that belong to a class. They always take `self` as the first parameter:

```python
class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed
        self.tricks = []  # Default value

    def bark(self):
        return f"{self.name} says Woof!"

    def learn_trick(self, trick):
        self.tricks.append(trick)
        return f"{self.name} learned {trick}!"

# Using the methods
my_dog = Dog("Buddy", "Golden Retriever")
print(my_dog.bark())               # "Buddy says Woof!"
print(my_dog.learn_trick("sit"))   # "Buddy learned sit!"
print(my_dog.learn_trick("roll"))  # "Buddy learned roll!"
print(my_dog.tricks)               # ["sit", "roll"]
```

Notice how methods can access and modify the object's attributes via `self`.

---

## Class vs. Instance Attributes

Attributes defined directly in the class body (not inside `__init__`) are **shared** by all instances:

```python
class Dog:
    species = "Canis familiaris"  # Class attribute — shared by all dogs

    def __init__(self, name):
        self.name = name          # Instance attribute — unique to each dog

d1 = Dog("Buddy")
d2 = Dog("Luna")

print(d1.species)  # "Canis familiaris"
print(d2.species)  # "Canis familiaris" (same)
print(d1.name)     # "Buddy" (different)
print(d2.name)     # "Luna" (different)
```

---

## Special (Dunder) Methods

Methods that start and end with double underscores (`__`) are called **dunder methods** (double underscore). Python uses them for built-in operations like `print()`, `len()`, `+`, etc.

```python
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def __str__(self):        # What print() shows
        return f"'{self.title}' by {self.author}"

    def __len__(self):        # What len() returns
        return self.pages

    def __eq__(self, other):  # What == compares
        return self.title == other.title and self.author == other.author

book = Book("Python 101", "Alice", 300)
print(book)     # 'Python 101' by Alice  (from __str__)
print(len(book))  # 300                   (from __len__)
```

---

## Inheritance

**Inheritance** lets you create a new class that reuses attributes and methods from an existing class:

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):          # Dog inherits from Animal
    def speak(self):        # Override the parent method
        return f"{self.name} says Woof!"

class Cat(Animal):          # Cat inherits from Animal
    def speak(self):
        return f"{self.name} says Meow!"

# Both share the __init__ from Animal
dogs = [Dog("Buddy"), Dog("Luna")]
cats = [Cat("Whiskers")]

for animal in dogs + cats:
    print(animal.speak())   # Each knows how to speak its own way
```

This is **polymorphism** — different classes implement the same method in different ways, and you can treat them uniformly.

---

## A Practical Example

Let's model a bank account:

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.__balance = balance  # Private attribute (name mangled)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive!")
        self.__balance += amount
        return f"Deposited ${amount}. Balance: ${self.__balance}"

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal must be positive!")
        if amount > self.__balance:
            raise ValueError("Insufficient funds!")
        self.__balance -= amount
        return f"Withdrew ${amount}. Balance: ${self.__balance}"

    def get_balance(self):  # Read-only access to balance
        return self.__balance

account = BankAccount("Alice", 100)
print(account.deposit(50))     # "Deposited $50. Balance: $150"
print(account.withdraw(30))    # "Withdrew $30. Balance: $120"
# print(account.__balance)     # Error! Attribute is "private"
```

Attributes starting with `__` get **name-mangled** to discourage direct access — a convention for private data.

---

## Try It Yourself

1. Create a `Student` class with `name`, `grade`, and a method `introduce()` that prints `"Hi, I'm [name] and I'm in grade [grade]."`
2. Add a `__str__` method to your `Student` class so that `print(student)` shows a nice description.
3. Create a `GraduateStudent` class that inherits from `Student` and adds a `thesis_topic` attribute.

---

## Common Mistakes

- **Forgetting `self`:** Every instance method must take `self` as the first argument.
- **Forgetting `self.` prefix:** Inside methods, use `self.name` to access attributes, not just `name`.
- **Confusing class and instance attributes:** Data that varies per instance belongs in `__init__`.
- **Modifying mutable class attributes:** A list as a class attribute is shared by all instances — which is rarely what you want.

---

## Summary

- A **class** is a blueprint; an **object** is an instance of a class
- `__init__` sets up the initial state of an object
- `self` refers to the current instance
- **Methods** are functions inside a class
- **Class attributes** are shared; **instance attributes** belong to one object
- **Dunder methods** (`__str__`, `__len__`, etc.) hook into Python's built-in behavior
- **Inheritance** lets one class reuse and extend another
