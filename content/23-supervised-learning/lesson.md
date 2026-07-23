# Lesson 23: Supervised Learning — Regression & Classification

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Explain the difference between regression and classification
> - Train a linear regression model using scikit-learn
> - Train a classification model using k-Nearest Neighbors
> - Evaluate model performance with appropriate metrics
> - Make predictions on new data

---

## Supervised Learning

In **supervised learning**, you have a dataset with input features and known output labels. The model learns the mapping from inputs to outputs so it can predict labels for new, unseen data.

**Two main tasks:**

| Task | Output | Example |
|------|--------|---------|
| **Regression** | Continuous number | Predict house price: $350,000 |
| **Classification** | Category/class | Predict email type: "spam" or "not spam" |

---

## Installing scikit-learn

scikit-learn is the most popular Python library for classical machine learning:

```bash
pip install scikit-learn
```

It provides consistent APIs for dozens of algorithms — once you know one, you know them all.

---

## Regression: Predicting Continuous Values

### Linear Regression

Linear regression finds the best-fit line through your data: `y = mx + b`

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# Training data: house sizes (sq ft) and prices
X = np.array([600, 800, 1000, 1200, 1400]).reshape(-1, 1)
y = np.array([150, 180, 220, 260, 300])  # Price in $1000s

# Create and train the model
model = LinearRegression()
model.fit(X, y)

# Make a prediction
prediction = model.predict([[1100]])   # 1100 sq ft house
print(f"Predicted price for 1100 sq ft: ${prediction[0]*1000:.0f}")

# Model parameters
print(f"Coefficient (slope): {model.coef_[0]:.2f}")
print(f"Intercept: {model.intercept_:.2f}")  # y = slope * x + intercept
```

### Evaluating Regression

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Predict on the same training data (just for illustration)
y_pred = model.predict(X)

print(f"MAE:  {mean_absolute_error(y, y_pred):.2f}")   # Mean Absolute Error
print(f"RMSE: {np.sqrt(mean_squared_error(y, y_pred)):.2f}")  # Root Mean Squared Error
print(f"R²:   {r2_score(y, y_pred):.3f}")              # R-squared (1.0 = perfect)
```

- **MAE:** Average error in the same units as the target (e.g., $ thousands)
- **RMSE:** Similar to MAE but penalizes large errors more
- **R²:** Proportion of variance explained by the model (1.0 = perfect, 0.0 = no better than mean)

---

## Classification: Predicting Categories

### k-Nearest Neighbors (k-NN)

k-NN predicts the class of a data point by looking at the `k` closest training examples and taking a majority vote.

```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

# Sample data: [weight, sweetness] for fruits
X = np.array([[150, 7], [160, 8], [130, 5],         # Apples
              [180, 3], [190, 2], [200, 4],          # Oranges
              [50,  9], [60,  8], [55,  7]])         # Grapes
y = np.array(["apple", "apple", "apple",
              "orange", "orange", "orange",
              "grape", "grape", "grape"])

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=42
)

# Create and train the model
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)

# Make predictions
predictions = knn.predict(X_test)
print(f"Predictions: {predictions}")
print(f"Actual:      {y_test}")

# Evaluate accuracy
accuracy = knn.score(X_test, y_test)
print(f"Accuracy: {accuracy:.0%}")
```

### Classification Metrics

```python
from sklearn.metrics import accuracy_score, classification_report

# Accuracy: percentage of correct predictions
print(f"Accuracy: {accuracy_score(y_test, predictions):.0%}")

# Detailed report (precision, recall, f1-score for each class)
print(classification_report(y_test, predictions))
```

- **Precision:** Of the items predicted as class X, how many were correct?
- **Recall:** Of the actual class X items, how many did we catch?
- **F1-score:** Harmonic mean of precision and recall

---

## The Complete Workflow

```python
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# 1. Prepare data
X = np.random.randn(150, 4)  # 150 samples, 4 features
y = (X[:, 0] + X[:, 1] > 0).astype(int)  # Binary label

# 2. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. Scale features (crucial for k-NN!)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Use same scaler

# 4. Train
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train_scaled, y_train)

# 5. Evaluate
y_pred = knn.predict(X_test_scaled)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")
```

**Why scaling is crucial for k-NN:** k-NN uses distance to find neighbors. If one feature (e.g., salary in $) is much larger than another (e.g., age), it dominates the distance calculation.

---

## Common Mistakes

- **Scaling after split:** Fit the scaler on training data only, then transform test data.
- **Evaluating on training data:** High training accuracy + low test accuracy = overfitting.
- **Wrong k value:** Too small = noisy predictions; too large = oversmoothing. Try k=3, 5, 7.
- **For categorical features:** scikit-learn needs numerical input. Use one-hot encoding for categories.

---

## Try It Yourself

1. Create a small dataset of 20 samples with 2 features: `hours_studied` and `hours_slept`
2. Create labels: `1` if passed (hours_studied > 5), `0` otherwise
3. Split into training (80%) and test (20%) sets
4. Train a k-NN classifier (k=3)
5. Evaluate accuracy on the test set

---

## Summary

- **Supervised learning** learns from labeled data
- **Regression** predicts continuous values (Linear Regression)
- **Classification** predicts categories (k-Nearest Neighbors)
- **scikit-learn** provides a consistent `.fit() → .predict() → .score()` workflow
- Always **scale features** for distance-based algorithms like k-NN
- Use **train/test split** to evaluate real-world performance
- Key metrics: MAE/RMSE/R² for regression, accuracy for classification
