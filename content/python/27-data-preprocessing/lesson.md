# Lesson 27: Data Preprocessing

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Identify and handle missing data in datasets
> - Scale numerical features using normalization and standardization
> - Split data into training and testing sets
> - Understand why preprocessing is critical for ML model performance

---

## Why Preprocess Data?

Real-world data is messy. It has missing values, inconsistent formats, and features on wildly different scales. Feeding raw data into a machine learning model will give you poor results — or no results at all.

**Data preprocessing** is the step where you clean and transform raw data into a format the model can learn from. It's often said that 80% of a data scientist's time is spent on data preparation.

---

## Handling Missing Data

Missing values appear as `NaN` (Not a Number), `None`, or empty strings in your data.

### Detecting Missing Values

```python
import numpy as np

data = np.array([1.0, 2.0, np.nan, 4.0, np.nan, 6.0])

print(np.isnan(data))  # [False False  True False  True False]
print(data[np.isnan(data)])  # The NaN values themselves
```

### Option 1: Remove Missing Values

If you have plenty of data, simply drop rows with missing values:

```python
# Keep only valid (non-NaN) values
clean_data = data[~np.isnan(data)]
print(clean_data)  # [1. 2. 4. 6.]
```

Use this when:
- You have enough data that dropping a few rows won't hurt
- The missing values are random (not systematic)

### Option 2: Fill Missing Values (Imputation)

Replace missing values with a reasonable estimate:

```python
# Fill with the mean
mean_val = np.nanmean(data)  # Mean ignoring NaN
filled = np.where(np.isnan(data), mean_val, data)
print(filled)  # [1.  2.  3.25  4.  3.25  6. ]

# Fill with the median (more robust to outliers)
median_val = np.nanmedian(data)
filled_median = np.where(np.isnan(data), median_val, data)
```

For 2D data, you might fill column-wise:

```python
matrix = np.array([[1, np.nan, 3],
                   [4, 5, np.nan],
                   [7, 8, 9]])

# Fill each column's NaN with that column's mean
col_mean = np.nanmean(matrix, axis=0)
for col in range(matrix.shape[1]):
    mask = np.isnan(matrix[:, col])
    matrix[mask, col] = col_mean[col]
```

---

## Feature Scaling

Machine learning models are sensitive to the scale of features. Consider:

- **Feature A:** Age (0–100)
- **Feature B:** Salary (0–200,000)

A model might treat salary as more important simply because its numbers are larger. Scaling fixes this.

### Normalization (Min-Max Scaling)

Scales values to a fixed range, usually [0, 1]:

```python
data = np.array([10, 20, 30, 40, 50], dtype=float)

normalized = (data - data.min()) / (data.max() - data.min())
print(normalized)  # [0.   0.25 0.5  0.75 1.  ]
```

### Standardization (Z-Score Scaling)

Centers values around 0 with a standard deviation of 1:

```python
standardized = (data - data.mean()) / data.std()
print(standardized)  # [-1.41 -0.71  0.    0.71  1.41]
```

**Which to use?**

| Method | When |
|--------|------|
| **Normalization [0,1]** | When data doesn't follow a normal distribution, or you need bounded values |
| **Standardization (Z-score)** | When data has outliers, or the algorithm assumes normal distribution (e.g., linear regression, SVM) |

---

## Train/Test Split

You never train a model on all your data — it needs to be tested on data it hasn't seen. The standard approach: split into **training** and **testing** sets.

```python
import numpy as np

# Sample data: 100 samples, each with 3 features
X = np.random.rand(100, 3)  # Features
y = np.random.randint(0, 2, 100)  # Labels (0 or 1)

# Shuffle and split (80% train, 20% test)
np.random.seed(42)  # For reproducible results
indices = np.random.permutation(len(X))
split_point = int(0.8 * len(X))

train_idx = indices[:split_point]
test_idx = indices[split_point:]

X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
```

**Why a random seed?** Setting `np.random.seed(42)` ensures you get the same split every time you run the code — essential for reproducible experiments.

---

## Putting It All Together

```python
import numpy as np

# Raw dataset: [age, salary, years_experience]
raw_data = np.array([
    [25, 50000, 2],
    [30, np.nan, 5],
    [35, 75000, np.nan],
    [40, 100000, 15],
    [np.nan, 60000, 3],
])

# Step 1: Handle missing values (fill with column means)
col_means = np.nanmean(raw_data, axis=0)
for col in range(raw_data.shape[1]):
    mask = np.isnan(raw_data[:, col])
    raw_data[mask, col] = col_means[col]

# Step 2: Standardize features
X = raw_data.copy()
means = X.mean(axis=0)
stds = X.std(axis=0)
X_standardized = (X - means) / stds

# Step 3: Train/test split
np.random.seed(42)
indices = np.random.permutation(len(X_standardized))
split = int(0.8 * len(X_standardized))
X_train = X_standardized[indices[:split]]
X_test = X_standardized[indices[split:]]

print("Training data (standardized):")
print(X_train)
print(f"\nFeature means after scaling: {X_train.mean(axis=0).round(2)}")
print(f"Feature stds after scaling:  {X_train.std(axis=0).round(2)}")
```

After standardization, each feature has mean ≈ 0 and std ≈ 1 — the model can now learn fairly from all features.

---

## Common Mistakes

- **Scaling before split:** Always compute scaling parameters (mean, std) on the training set, then apply them to the test set. Never use test data to compute scaling values.
- **Filling with 0:** Filling missing values with 0 is rarely appropriate — use mean, median, or a more sophisticated method.
- **Forgetting NaN-safe functions:** Use `np.nanmean()`, `np.nanmedian()` etc. instead of `np.mean()` when your data contains NaN.
- **Not shuffling:** Always shuffle before splitting to avoid ordering bias.

---

## Try It Yourself

1. Create a NumPy array with some NaN values
2. Fill the NaN values with the column means
3. Normalize the data to [0, 1] range
4. Split into training (80%) and testing (20%) sets

---

## Summary

- **Missing data** is common — detect with `np.isnan()`, handle by removing or imputing
- **Feature scaling** (normalization or standardization) prevents features with larger numbers from dominating
- **Train/test split** (typically 80/20) ensures you evaluate on unseen data
- Always fit scaling parameters on the **training set** and transform the **test set** with those same parameters
- Use `np.random.seed()` for reproducible results
