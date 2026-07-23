# Lesson 23: Introduction to Machine Learning & NumPy

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Explain what machine learning is and the difference between supervised and unsupervised learning
> - Install and import NumPy
> - Create and manipulate NumPy arrays
> - Perform element-wise operations on arrays
> - Understand why NumPy is faster than Python lists for numerical data

---

## What is Machine Learning?

Machine Learning (ML) is a way to teach computers to learn from data without explicitly programming every rule. Instead of writing `if rainfall > 50: umbrella = True`, you show the computer thousands of examples of weather data and whether people took umbrellas, and it figures out the pattern itself.

**Two main types of ML:**

| Type | What it does | Example |
|------|-------------|---------|
| **Supervised Learning** | Learns from labeled data (input → output pairs) | Predict house price from size, bedrooms, location |
| **Unsupervised Learning** | Finds patterns in unlabeled data | Group customers by purchasing behavior |

We'll explore both types in the coming lessons. First, we need the right tools for numerical computing.

---

## Why NumPy?

Python lists are great, but they're slow for mathematical operations. NumPy (Numerical Python) introduces **arrays** — objects designed for fast numerical computation.

```python
import numpy as np

# Python list
py_list = [1, 2, 3, 4, 5]
doubled = [x * 2 for x in py_list]  # 5 operations, one at a time

# NumPy array
np_array = np.array([1, 2, 3, 4, 5])
doubled = np_array * 2              # One operation on the whole array!
```

NumPy is the foundation for almost every Python data science library: pandas, scikit-learn, TensorFlow, and PyTorch all build on it.

**Install it:**

```bash
pip install numpy
```

---

## Creating NumPy Arrays

```python
import numpy as np

# From a list
arr = np.array([1, 2, 3, 4, 5])
print(arr)        # [1 2 3 4 5]
print(type(arr))  # <class 'numpy.ndarray'>

# 2D array (matrix)
matrix = np.array([[1, 2, 3], [4, 5, 6]])
print(matrix)
# [[1 2 3]
#  [4 5 6]]

# Special arrays
zeros = np.zeros((3, 3))     # 3x3 array of zeros
ones = np.ones((2, 4))       # 2x4 array of ones
range_arr = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5)  # [0.0, 0.25, 0.5, 0.75, 1.0]

# Random arrays
random_arr = np.random.rand(3, 3)      # Uniform random [0, 1)
randn_arr = np.random.randn(100)       # Normal distribution (mean=0, std=1)
```

---

## Array Operations

### Element-wise Math

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(a + b)    # [5 7 9]
print(a * b)    # [4 10 18]
print(a ** 2)   # [1 4 9]
print(np.sqrt(a))  # [1.0, 1.41, 1.73]
```

### Aggregation

```python
data = np.array([[1, 2, 3], [4, 5, 6]])

print(data.sum())       # 21 (sum of all elements)
print(data.mean())      # 3.5 (average)
print(data.max())       # 6
print(data.min())       # 1
print(data.std())       # 1.70 (standard deviation)

# Sum along an axis
print(data.sum(axis=0))  # [5 7 9]   (sum columns)
print(data.sum(axis=1))  # [6 15]    (sum rows)
```

### Indexing and Slicing

```python
arr = np.array([10, 20, 30, 40, 50])
print(arr[0])       # 10
print(arr[1:3])     # [20 30]
print(arr[::-1])    # [50 40 30 20 10] (reversed)

# 2D indexing
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(matrix[1, 2])     # 6 (row 1, column 2)
print(matrix[0:2, 1:])  # [[2 3]
                        #  [5 6]]
```

### Boolean Masking

```python
scores = np.array([85, 92, 78, 95, 88])
above_90 = scores > 90
print(above_90)                  # [False  True False  True False]
print(scores[scores > 90])       # [92 95]
print(scores[(scores >= 80) & (scores < 90)])  # [85 88]
```

Boolean masking is incredibly powerful — it lets you filter data without writing loops.

---

## Why NumPy is Fast

NumPy arrays are stored in **contiguous memory blocks** (like a C array), and operations are implemented in C/Fortran. A Python list stores **pointers to objects** scattered across memory.

```python
import time

# Python list
py_list = list(range(1_000_000))
start = time.time()
result = [x * 2 for x in py_list]
print(f"Python list: {time.time() - start:.3f}s")

# NumPy array
np_arr = np.arange(1_000_000)
start = time.time()
result = np_arr * 2
print(f"NumPy array: {time.time() - start:.3f}s")
```

On a typical machine, NumPy is **10-50x faster** than Python lists for numerical operations.

---

## Common Mistakes

- **Mixing types:** NumPy arrays have a single data type. `np.array([1, 2, 3.0])` converts all to float.
- **Forgetting to import:** Always `import numpy as np` at the top of your file.
- **Confusing axis:** `axis=0` operates vertically (rows), `axis=1` operates horizontally (columns).
- **Not installing:** Run `pip install numpy` before your first `import numpy`.

---

## Try It Yourself

1. Create a NumPy array with the numbers 1 to 20
2. Reshape it into a 4×5 matrix
3. Calculate the mean of each column (axis=0)
4. Extract all values greater than 10
5. Create a random 3×3 array and find its maximum value

---

## Summary

- **Machine Learning** lets computers learn patterns from data
- **Supervised** = learns from labeled examples; **Unsupervised** = finds hidden patterns
- **NumPy** is Python's fundamental library for numerical computing
- **Arrays** are faster and more memory-efficient than Python lists
- Use **element-wise operations**, **aggregation**, and **boolean masking** to work with data
- NumPy is the foundation for pandas, scikit-learn, and all ML libraries
