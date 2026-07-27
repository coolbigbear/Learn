# Exercise Authoring Guide: `test_suite` (Unit-Test Style)

> **Audience:** Content authors writing or migrating exercises for the Python track.
> **Status:** Living document — update as the system evolves.

---

## 1. Overview

### What is a `test_suite` exercise?

A **test_suite** exercise asks the student to **implement a function or class** (or any callable component) and validates it by running a set of **unit-test-style assertions** against their code. The student's code is imported as a Python module, and the platform runs a separate test suite that calls their functions and asserts expected behaviour.

This is the same model used by HackerRank, LeetCode, and Codewars — the student writes a reusable component, not a throwaway script.

### How it differs from `test_cases`

The existing **`test_cases`** (output-comparison) model works like this:

1. The student's entire script is executed.
2. The harness captures everything printed to stdout.
3. It compares stdout against expected output (exact match, regex, contains, etc.).

This works for simple exercises, but it has serious limitations:

- Students must use `print()` to produce output, which mixes **implementation** with **presentation**.
- It can only test the **final output**, not intermediate values or multiple scenarios.
- It forces a single run — you can't test a function with five different inputs.
- It makes class-method and property-based exercises awkward (students print things instead of returning them).

**`test_suite` solves these problems:**

- The student writes a **pure component** (function, class, method) that returns values.
- The test suite imports that component and calls it with various arguments.
- Each `test_*` function is a separate test that can check different behaviours.
- Tests report rich assertion messages, not just "expected X, got Y".

### When to use which model

| Exercise type | Model | Example |
|---|---|---|
| Implement a function that returns a value | `test_suite` | `def add(a, b): return a + b` |
| Implement a class with methods | `test_suite` | `class Student: def introduce(self): ...` |
| Write a script that produces output | `test_cases` | `print("Hello, World!")` |
| Write code that reads from stdin | `test_cases` | `name = input(); print(f"Hi, {name}")` |
| Check code structure (contains a comment, uses `for`) | `test_cases` (code_contains) | Ensure the word "while" appears in the code |
| Fix a bug in existing code that prints specific output | `test_cases` | Debugging exercise with known output |
| Capstone project component | `test_suite` | Build a FastAPI endpoint or XML parser module |

**Rule of thumb:** If the exercise asks the student to `return` a value, use `test_suite`. If it asks the student to `print()` or `input()`, use `test_cases`.

---

## 2. JSON Format

A `test_suite` exercise looks like this in the exercises JSON file:

```json
{
  "slug": "func-add",
  "title": "Addition function",
  "instruction": "Define a function `add(a, b)` that **returns** the sum of a and b.",
  "starter_code": "def add(a, b):\n    # Return the sum of a and b\n    pass",
  "test_suite": "def test_adds_two_positive():\n    result = add(7, 12)\n    assert result == 19\n\ndef test_adds_zero():\n    result = add(0, 5)\n    assert result == 5\n\ndef test_adds_negative():\n    result = add(-3, 10)\n    assert result == 7\n\ndef test_both_negative():\n    result = add(-5, -7)\n    assert result == -12",
  "solution_code": "def add(a, b):\n    return a + b",
  "test_cases": [],
  "order": 1
}
```

### Field reference

| Field | Required | Type | Description |
|---|---|---|---|
| `slug` | Yes | string | Unique identifier within the lesson (kebab-case). |
| `title` | Yes | string | Short human-readable title (shown in exercise tabs). |
| `instruction` | Yes | string | What the student must do. Can include markdown formatting. |
| `starter_code` | Yes | string | Code shown in the editor. Should include `#` comments prompting the student. |
| `test_suite` | No | string or null | **Python code only** — unit-test functions that validate the student's code. |
| `solution_code` | Yes | string | The complete correct solution. Used for reference and automated verification. |
| `test_cases` | Yes | array | Must be `[]` when `test_suite` is present (kept for backward compatibility). |
| `order` | Yes | integer | 1-based position within the lesson. |

### Key structural rules

- **`test_suite` must be a plain Python string** — no markdown, no JSON wrapping.
- **`test_cases` must be `[]`** when `test_suite` is provided (the system uses one or the other).
- **Escaping:** Use `\n` for newlines inside the JSON string. Use `\\` for literal backslashes in the Python code (e.g., `\\\"` inside f-strings).

---

## 3. Rules

### 3.1 `test_suite` contains Python code only

The string in `test_suite` is passed directly to the Python exec() inside the sandbox. Do not include:

- Markdown formatting (\`\`\`python ... \`\`\`)
- JSON wrapping or extra delimiters
- HTML or explanatory comments that aren't valid Python

**Correct:**
```python
def test_adds_two_positive():
    result = add(7, 12)
    assert result == 19
```

**Incorrect (don't do this):**
```python
```python
def test_adds_two_positive():
    result = add(7, 12)
    assert result == 19
```
```

### 3.2 Functions named `test_*` are auto-discovered

The harness scans the test suite namespace for callable objects whose names start with `test_`. Each one becomes a separate test result displayed to the student.

```python
# These are discovered:
def test_adds_positive():
    ...

def test_adds_negative():
    ...

def test_edge_case_empty_string():
    ...

# These are NOT discovered:
def helper_function():
    ...                     # doesn't start with test_

class Tests:
    def test_something(self):
        ...                 # bound method, not top-level callable
```

### 3.3 Each test function uses plain `assert` statements

Use Python's built-in `assert` keyword. The assertion's condition determines pass/fail.

```python
assert add(2, 3) == 5          # passes if add returns 5
assert len(result) > 0         # passes if result is non-empty
assert isinstance(obj, dict)   # passes if obj is a dict
```

When an assertion fails, Python raises `AssertionError`. The harness catches this and records the test as failed.

### 3.4 Assertion messages are optional but strongly recommended

Add a message after the assertion to provide human-readable failure feedback:

```python
assert result == 19, f"Expected 19, but got {result}"
assert student.grade == 10, f"Expected grade 10, got {student.grade}"
assert "error" in result.lower(), f"Expected 'error' in response: {result}"
```

**Why this matters:** The assertion message is what the student sees in the feedback panel. Without a message, they only see "AssertionError" — not helpful. With a good message, they immediately understand what went wrong.

**Recommendation:** Always include an assertion message that mentions:
- What was expected
- What was actually received
- The context (which function, which input)

### 3.5 User code is accessed through the `exercise` namespace

The student's code is saved to a file called `exercise.py`, imported as a Python module, and made available to the test suite as `exercise`.

```python
# Student writes:
def add(a, b):
    return a + b

# Test suite accesses:
def test_add():
    result = exercise.add(7, 12)     # ← use 'exercise.' prefix
    assert result == 19
```

**Always use `exercise.` to access the student's functions, classes, and variables.**

```python
# For a class exercise:
s = exercise.Student("Alice", 10)
assert s.introduce() == "Hi, I'm Alice and I'm in grade 10."

# For a variable exercise:
assert exercise.PI == 3.14159

# For a function exercise:
result = exercise.calculate_mean([1, 2, 3, 4, 5])
assert result == 3.0
```

### 3.6 No side effects at import time

Because the student's code is imported as a module, any top-level code runs immediately when the module loads. **Avoid exercises where the student's code has top-level side effects** (e.g., prints something, reads a file, starts a server) unless those side effects are the point of the exercise.

The starter code should **not** include `print()` calls or `input()` calls at the top level — those belong in `test_cases` exercises, not `test_suite` exercises.

---

## 4. Examples

### 4.1 Basic: function returning a value

**Instruction:** Define a function `is_even(n)` that returns `True` if `n` is even, and `False` otherwise.

```json
{
  "slug": "is-even",
  "title": "Even number check",
  "instruction": "Define a function `is_even(n)` that returns `True` if `n` is even, and `False` otherwise.",
  "starter_code": "def is_even(n):\n    # Return True if n is even, False otherwise\n    pass",
  "test_suite": "def test_even_number():\n    result = exercise.is_even(4)\n    assert result == True, f\"Expected True for 4, got {result}\"\n\ndef test_odd_number():\n    result = exercise.is_even(7)\n    assert result == False, f\"Expected False for 7, got {result}\"\n\ndef test_zero():\n    result = exercise.is_even(0)\n    assert result == True, f\"Expected True for 0, got {result}\"",
  "solution_code": "def is_even(n):\n    return n % 2 == 0",
  "test_cases": []
}
```

### 4.2 Multiple test functions for the same exercise

**Instruction:** Define a function `reverse_string(s)` that returns the reverse of string `s`.

```json
{
  "slug": "reverse-string",
  "title": "Reverse a string",
  "instruction": "Define a function `reverse_string(s)` that returns the reverse of string `s`.",
  "starter_code": "def reverse_string(s):\n    # Return the reversed string\n    pass",
  "test_suite": "def test_reverse_basic():\n    result = exercise.reverse_string(\"hello\")\n    assert result == \"olleh\", f\"Expected 'olleh', got {result!r}\"\n\ndef test_reverse_single_char():\n    result = exercise.reverse_string(\"a\")\n    assert result == \"a\", f\"Expected 'a', got {result!r}\"\n\ndef test_reverse_even_length():\n    result = exercise.reverse_string(\"abcd\")\n    assert result == \"dcba\", f\"Expected 'dcba', got {result!r}\"\n\ndef test_reverse_with_spaces():\n    result = exercise.reverse_string(\"hi there\")\n    assert result == \"ereht ih\", f\"Expected 'ereht ih', got {result!r}\"",
  "solution_code": "def reverse_string(s):\n    return s[::-1]",
  "test_cases": []
}
```

### 4.3 Testing with multiple arguments

**Instruction:** Define a function `calculate_mean(numbers)` that takes a list of numbers and returns their mean.

```json
{
  "slug": "calculate-mean",
  "title": "Calculate the mean",
  "instruction": "Define a function `calculate_mean(numbers)` that takes a list of numbers and returns their **mean** (average).",
  "starter_code": "def calculate_mean(numbers):\n    # Return the mean of the numbers\n    pass",
  "test_suite": "def test_mean_of_positive():\n    result = exercise.calculate_mean([1, 2, 3, 4, 5])\n    assert result == 3.0, f\"Expected 3.0, got {result}\"\n\ndef test_mean_of_single():\n    result = exercise.calculate_mean([42])\n    assert result == 42.0, f\"Expected 42.0, got {result}\"\n\ndef test_mean_with_negative():\n    result = exercise.calculate_mean([-5, 0, 5])\n    assert result == 0.0, f\"Expected 0.0, got {result}\"\n\ndef test_mean_of_floats():\n    result = exercise.calculate_mean([1.5, 2.5, 3.0])\n    assert result == 7.0 / 3.0, f\"Expected {7.0/3.0}, got {result}\"",
  "solution_code": "def calculate_mean(numbers):\n    return sum(numbers) / len(numbers)",
  "test_cases": []
}
```

### 4.4 Testing class methods

**Instruction:** Create a `BankAccount` class with `__init__(self, owner, balance=0)`, a `deposit(amount)` method, and a `withdraw(amount)` method that returns `True` if successful or `False` if insufficient funds.

```json
{
  "slug": "bank-account",
  "title": "Bank Account class",
  "instruction": "Create a `BankAccount` class with:\n- `__init__(self, owner, balance=0)` — sets owner name and starting balance\n- `deposit(amount)` — adds to balance, returns the new balance\n- `withdraw(amount)` — subtracts if sufficient funds, returns `True` if successful, `False` if insufficient",
  "starter_code": "class BankAccount:\n    def __init__(self, owner, balance=0):\n        pass\n    \n    def deposit(self, amount):\n        pass\n    \n    def withdraw(self, amount):\n        pass",
  "test_suite": "def test_initial_balance():\n    acct = exercise.BankAccount(\"Alice\", 100)\n    assert acct.balance == 100, f\"Expected balance 100, got {acct.balance}\"\n\ndef test_deposit():\n    acct = exercise.BankAccount(\"Bob\", 50)\n    result = acct.deposit(25)\n    assert result == 75, f\"Expected 75 after deposit, got {result}\"\n    assert acct.balance == 75, f\"Expected balance 75, got {acct.balance}\"\n\ndef test_successful_withdraw():\n    acct = exercise.BankAccount(\"Charlie\", 200)\n    result = acct.withdraw(50)\n    assert result == True, f\"Expected True for successful withdrawal, got {result}\"\n    assert acct.balance == 150, f\"Expected balance 150, got {acct.balance}\"\n\ndef test_insufficient_funds():\n    acct = exercise.BankAccount(\"Diana\", 30)\n    result = acct.withdraw(100)\n    assert result == False, f\"Expected False for insufficient funds, got {result}\"\n    assert acct.balance == 30, f\"Balance should remain 30 after failed withdrawal, got {acct.balance}\"\n\ndef test_default_balance():\n    acct = exercise.BankAccount(\"Eve\")\n    assert acct.owner == \"Eve\", f\"Expected owner 'Eve', got {acct.owner!r}\"\n    assert acct.balance == 0, f\"Expected default balance 0, got {acct.balance}\"",
  "solution_code": "class BankAccount:\n    def __init__(self, owner, balance=0):\n        self.owner = owner\n        self.balance = balance\n\n    def deposit(self, amount):\n        self.balance += amount\n        return self.balance\n\n    def withdraw(self, amount):\n        if amount <= self.balance:\n            self.balance -= amount\n            return True\n        return False",
  "test_cases": []
}
```

### 4.5 Testing with edge cases

**Instruction:** Define a function `safe_divide(a, b)` that returns `a` divided by `b`. If `b` is zero, return `None` instead of raising an error.

```json
{
  "slug": "safe-divide",
  "title": "Safe division",
  "instruction": "Define a function `safe_divide(a, b)` that returns `a / b`. If `b` is zero, return `None` instead of raising an error.",
  "starter_code": "def safe_divide(a, b):\n    # Return a / b, or None if b is 0\n    pass",
  "test_suite": "def test_normal_division():\n    result = exercise.safe_divide(10, 2)\n    assert result == 5.0, f\"Expected 5.0, got {result}\"\n\ndef test_divide_by_one():\n    result = exercise.safe_divide(99, 1)\n    assert result == 99.0, f\"Expected 99.0, got {result}\"\n\ndef test_divide_zero_by_number():\n    result = exercise.safe_divide(0, 5)\n    assert result == 0.0, f\"Expected 0.0, got {result}\"\n\ndef test_divide_by_zero():\n    result = exercise.safe_divide(42, 0)\n    assert result is None, f\"Expected None for division by zero, got {result}\"\n\ndef test_negative_division():\n    result = exercise.safe_divide(-15, 3)\n    assert result == -5.0, f\"Expected -5.0, got {result}\"\n\ndef test_boundary_very_large():\n    result = exercise.safe_divide(10**6, 0.5)\n    assert result == 2 * 10**6, f\"Expected {2 * 10**6}, got {result}\"",
  "solution_code": "def safe_divide(a, b):\n    if b == 0:\n        return None\n    return a / b",
  "test_cases": []
}
```

---

## 5. Conventions

### 5.1 When to use `test_suite` vs `test_cases`

| Criterion | `test_suite` | `test_cases` |
|---|---|---|
| **Student writes a function** | ✓ | ✗ (need print/input tricks) |
| **Student writes a class** | ✓ | ✗ (very awkward) |
| **Student writes a script** | ✗ | ✓ |
| **Testing stdout output** | ✗ | ✓ |
| **Testing stdin input** | ✗ | ✓ |
| **Multiple test scenarios** | ✓ (one per test_* function) | ✗ (one input/output pair) |
| **Code structure checks** | ✗ | ✓ (code_contains, comment, comment_contains) |
| **Regex on output** | ✗ | ✓ |
| **Edge case testing** | ✓ | ✗ (limited by single-run model) |
| **Capstone / real project** | ✓ | ✗ |

**Migration hint:** If you're rewriting a `test_cases` exercise and the instruction says "return" or "define a function", it's a candidate for `test_suite`. If the instruction says "print" or "display" or "write a program that", keep it as `test_cases`.

### 5.2 Naming conventions for test functions

Use descriptive, self-documenting names:

```python
# ✓ Good:
def test_returns_zero_for_empty_list():
def test_rejects_negative_age():
def test_deposit_increases_balance():
def test_empty_string_returns_none():

# ✗ Avoid:
def test_one():
def test_thing():
def test_a():
def test_():
```

**Pattern:** `test_<behaviour_or_scenario>`

This makes it clear which test failed when the student looks at the results.

### 5.3 Suggested template

Use this as a starting point for every `test_suite` exercise:

```json
{
  "slug": "your-exercise-slug",
  "title": "Your exercise title",
  "instruction": "Describe what the student should implement, with **markdown** for emphasis.",
  "starter_code": "def your_function(param):\n    # Describe what to do here\n    pass",
  "test_suite": "def test_happy_path():\n    result = exercise.your_function(...)\n    assert result == expected, f\"Expected {expected}, got {result}\"\n\ndef test_edge_case_empty():\n    result = exercise.your_function(...)\n    assert result == expected, f\"Expected {expected}, got {result}\"\n\ndef test_edge_case_boundary():\n    result = exercise.your_function(...)\n    assert result == expected, f\"Expected {expected}, got {result}\"",
  "solution_code": "def your_function(param):\n    # Complete correct implementation\n    return ...",
  "test_cases": []
}
```

**Template checklist:**

- [ ] `slug` is kebab-case and unique within the lesson
- [ ] `title` is concise but descriptive
- [ ] `instruction` uses markdown for code formatting (backticks), bold, etc.
- [ ] `starter_code` gives the student a clear starting point with `#` comments
- [ ] `test_suite` has **at least 3 test functions**: happy path + at least 2 edge cases
- [ ] Every test function has an assertion message
- [ ] `test_cases` is `[]`
- [ ] `solution_code` is the complete correct implementation

### 5.4 Test ordering and independence

- Test functions run in the order they appear in the `test_suite` string (sorted by definition order).
- Each test function runs independently — failures in one do not block others.
- However, tests share the same module import of the student's code, so **module-level side effects** in the student's code affect all tests.
- Design tests to be **independent**: each test should create its own instances, call its own functions, and not rely on state set up by a previous test.

---

## 6. Migration Checklist

When converting an existing `test_cases` exercise to `test_suite`:

- [ ] **Verify the exercise is a good candidate** — does the student implement a function/class that returns values? If it's a print/input script, keep it as `test_cases`.
- [ ] **Rewrite the instruction** — change from "Write a program that prints..." to "Define a function `xyz()` that returns...".
- [ ] **Rewrite the starter_code** — remove print() scaffolding, replace with a function signature and `pass`.
- [ ] **Write test functions** (see template above):
  - Happy path (expected use case)
  - At least 2 edge cases (empty input, zero, boundary values, type variations)
  - Error/exception cases if applicable
- [ ] **Assertion messages** — every assert has a descriptive message.
- [ ] **Set `test_cases: []`** — ensure the old test cases are cleared.
- [ ] **Verify `solution_code`** — matches the new signature and is a complete correct implementation.
- [ ] **Test the solution** — run the solution code against the test suite to confirm all tests pass. See Section 7 for how to do this.
- [ ] **Update `manifest.json`** — only if the lesson file path changed (rare).
- [ ] **PR description** — note that the exercise was migrated to `test_suite` format.

### Migration example: before and after

**Before (`test_cases` model):**
```json
{
  "slug": "greet-user",
  "title": "Greet the user",
  "instruction": "Ask the user for their name with `input()`, then print `\"Hello, [name]!\"`",
  "starter_code": "name = input()\n# Print the greeting\n",
  "test_cases": [
    {
      "input": "Alice",
      "expected_output": "Hello, Alice!\n",
      "comparison_type": "exact"
    }
  ],
  "solution_code": "name = input()\nprint(f\"Hello, {name}!\")\n"
}
```

**After (`test_suite` model) — only if we change to a function-based approach:**
```json
{
  "slug": "greet-user",
  "title": "Create a greeting function",
  "instruction": "Define a function `greet(name)` that returns `\"Hello, [name]!\"`.",
  "starter_code": "def greet(name):\n    # Return the greeting string\n    pass",
  "test_suite": "def test_greet_normal():\n    result = exercise.greet(\"Alice\")\n    assert result == \"Hello, Alice!\", f\"Expected 'Hello, Alice!', got {result!r}\"\n\ndef test_greet_empty():\n    result = exercise.greet(\"\")\n    assert result == \"Hello, !\", f\"Expected 'Hello, !', got {result!r}\"\n\ndef test_greet_with_numbers():\n    result = exercise.greet(\"User123\")\n    assert result == \"Hello, User123!\", f\"Expected 'Hello, User123!', got {result!r}\"",
  "solution_code": "def greet(name):\n    return f\"Hello, {name}!\"",
  "test_cases": []
}
```

**Better yet — keep the original as `test_cases` if interactivity (input/output) is the lesson focus.** Only migrate when the lesson goal is implementation.

---

## 7. Review Checklist (QA)

When reviewing a PR that adds or modifies `test_suite` exercises, check:

### Content correctness

- [ ] **All tests pass with the solution code** — run the solution against the test suite inside the sandbox.
- [ ] **All tests fail with the starter code** — the student's starting point should not accidentally pass any test.
- [ ] **Assertion messages are helpful** — they specify what was expected and what was received.
- [ ] **Test naming is descriptive** — each test name clearly describes the scenario.
- [ ] **No duplicate test scenarios** — each behaviour is tested exactly once.
- [ ] **Edge cases are covered** — empty input, zero, negative values, boundary values, type variations.
- [ ] **`test_cases` is `[]`** — no leftover output-comparison cases.

### Format

- [ ] **`test_suite` is plain Python code** — no markdown fences, no markdown formatting inside the string.
- [ ] **No escaping errors** — JSON `\n` is used for newlines, `\\` for backslashes, `\\\"` for quotes inside f-strings.
- [ ] **JSON is valid** — the exercises file parses correctly (no trailing commas, unquoted strings, etc.).
- [ ] **`exercise.` prefix is used** — the test suite accesses student code via `exercise.function_name()`.

### Pedagogy

- [ ] **Difficulty is appropriate** — the test suite matches the lesson level. Don't test advanced concepts in a beginner lesson.
- [ ] **Test suite doesn't give away the solution** — don't include the solution logic in test descriptions.
- [ ] **Happy path is tested first** — the first test function should be the most straightforward case.
- [ ] **Student-facing messages are clear** — a beginner should understand what failed and why.

### Technical verification

- [ ] **Run `python3 -c "exec(open('exercises.json').read())"`** — the JSON file parses as valid Python (for JSON file syntax check).
- [ ] **Run a dry import** — verify the test suite Python code is syntactically valid:
  ```bash
  python3 -c "
  import json
  with open('exercises.json') as f:
      data = json.load(f)
  for ex in data:
      if ex.get('test_suite'):
          compile(ex['test_suite'], '<test_suite>', 'exec')
          print(f'  ✓ {ex[\"slug\"]}: test_suite syntax OK')
  "```
- [ ] **If a seed re-import script exists**, run it to confirm the platform ingests the exercises correctly.

---

## Appendix A: Quick Reference

```
┌─────────────────────────────────────────────────────────────┐
│                    test_suite Quick Card                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  exercise. ─── prefix for all student code access           │
│  test_*   ─── function names to auto-discover               │
│  assert   ─── plain Python assertions only (no unittest)    │
│  f"..."   ─── assertion messages use f-strings              │
│  test_cases = [] ─── required when using test_suite         │
│                                                             │
│  Template:                                                   │
│  def test_<scenario>():                                      │
│      result = exercise.<function>(<args>)                    │
│      assert result == <expected>, f"..."                     │
│                                                             │
│  Min tests: 3 (happy path + 2 edge cases)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Appendix B: Common Mistakes

| Mistake | Why it's wrong | Fix |
|---|---|---|
| Forgetting `exercise.` prefix | `NameError: name 'add' is not defined` | Use `exercise.add(...)` |
| Using `unittest.TestCase` | The harness doesn't import unittest | Use plain `assert` |
| Including markdown in `test_suite` | SyntaxError or unexpected tokens | Keep it as **pure Python** |
| Leaving old `test_cases` populated | Both systems run, confusing results | Set `test_cases: []` |
| Using `print()` in tests | Print output is captured but not checked | Use `assert` for verification |
| Only one test function | Misses edge cases | Write at least 3 tests |
| No assertion message | Student sees bare "AssertionError" | Add a descriptive message: `assert ..., f"Expected X, got {actual}"` |
| Overly specific assertion messages | Brittle when solution changes | Describe the behaviour, not the implementation |
