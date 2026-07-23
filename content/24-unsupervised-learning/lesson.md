# Lesson 24: Unsupervised Learning & Mini ML Project

## Learning Objectives

> **By the end of this lesson, you will be able to:**
> - Explain unsupervised learning and when to use it
> - Implement K-Means clustering with scikit-learn
> - Determine the optimal number of clusters using the elbow method
> - Build a complete ML pipeline from raw data to insights

---

## Unsupervised Learning

In **unsupervised learning**, we have data **without labels**. The algorithm must find patterns, groupings, or structure on its own.

**Common tasks:**

| Task | What it does | Example |
|------|-------------|---------|
| **Clustering** | Group similar items together | Customer segmentation |
| **Dimensionality Reduction** | Simplify data while preserving structure | Data visualization |
| **Anomaly Detection** | Find unusual data points | Fraud detection |

We'll focus on **clustering** — the most common unsupervised technique.

---

## K-Means Clustering

K-Means groups data points into `k` clusters. Each point belongs to the cluster with the nearest center (centroid).

### How K-Means Works

1. Pick `k` random points as initial centroids
2. Assign each point to the nearest centroid
3. Move centroids to the mean of their assigned points
4. Repeat steps 2-3 until centroids stop moving

### Basic Usage

```python
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Generate sample data: three distinct groups
np.random.seed(42)
group1 = np.random.randn(30, 2) + [0, 0]     # Centered at (0, 0)
group2 = np.random.randn(30, 2) + [5, 5]     # Centered at (5, 5)
group3 = np.random.randn(30, 2) + [0, 5]     # Centered at (0, 5)

X = np.vstack([group1, group2, group3])

# Apply K-Means with 3 clusters
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
kmeans.fit(X)

# Get cluster assignments and centroids
labels = kmeans.labels_
centroids = kmeans.cluster_centers_

print(f"Cluster labels: {labels}")
print(f"Centroids:\n{centroids}")
```

### Visualizing Clusters

```python
# Scatter plot of the data colored by cluster
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', s=50)
plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroids')
plt.title('K-Means Clustering Results')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.legend()
plt.show()
```

---

## The Elbow Method: Finding the Right k

The hardest part of K-Means is choosing `k` — the number of clusters. The **elbow method** helps:

```python
import numpy as np
from sklearn.cluster import KMeans

X = np.random.randn(200, 2) + [0, 0]  # Your data

inertias = []
k_range = range(1, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)  # Sum of squared distances to centroids

# Plot elbow curve
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertias, 'bo-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal k')
plt.show()
```

Look for the **elbow** — the point where inertia stops dropping sharply. After that, adding more clusters gives diminishing returns.

```
Inertia
  |\
  | \
  |  \
  |   \____  ← elbow point (k=3 or 4)
  |       \___
  |           \____
  +------------------→ k
```

---

## Mini ML Project: Customer Segmentation

Let's put everything together — data preprocessing, scaling, clustering, and analysis.

### Step 1: Create Customer Data

```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

np.random.seed(42)

# Simulate customer data: [age, annual_income($), spending_score(1-100)]
n_customers = 200
age = np.random.randint(18, 70, n_customers)
income = np.random.randint(20000, 150000, n_customers)
spending = np.random.randint(1, 100, n_customers)

X = np.column_stack([age, income, spending])
```

### Step 2: Preprocess and Scale

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### Step 3: Find Optimal Clusters (Elbow Method)

```python
inertias = []
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Let's say the elbow is at k=4
optimal_k = 4
```

### Step 4: Apply K-Means

```python
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# Analyze each cluster
for cluster_id in range(optimal_k):
    mask = clusters == cluster_id
    print(f"\nCluster {cluster_id}: {mask.sum()} customers")
    print(f"  Avg Age:   {X[mask, 0].mean():.0f}")
    print(f"  Avg Income: ${X[mask, 1].mean():.0f}")
    print(f"  Avg Spending: {X[mask, 2].mean():.0f}/100")
```

### Step 5: Visualize with PCA

When you have more than 2 features, use PCA (Principal Component Analysis) to project down to 2D for visualization:

```python
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', s=50)
plt.title('Customer Segments (PCA-reduced view)')
plt.xlabel('First Principal Component')
plt.ylabel('Second Principal Component')
plt.colorbar(label='Cluster')
plt.show()
```

---

## Unsupervised vs Supervised — When to Use What?

| You have... | Use... | Example |
|------------|--------|---------|
| Labeled data, want to predict | **Supervised** (Regression/Classification) | Predict house prices |
| Unlabeled data, want to find groups | **Unsupervised** (Clustering) | Segment customers |
| Too many features, want to simplify | **Unsupervised** (PCA) | Reduce 1000 features to 10 |
| Few labeled + lots of unlabeled | **Semi-supervised** | Label propagation |

---

## Common Mistakes

- **Assuming clusters are spherical:** K-Means works best for circular/spherical clusters. For irregular shapes, try DBSCAN.
- **Guessing k:** Always use the elbow method or silhouette score to choose k.
- **Not scaling:** K-Means is distance-based — features with larger scales dominate.
- **Ignoring n_init:** Set `n_init=10` (or higher) to avoid poor local minima.

---

## Try It Yourself

1. Generate 100 random 2D points in two separate groups
2. Apply K-Means with k=2
3. Print the cluster labels and centroid positions
4. Predict which cluster a new point belongs to

---

## Summary

- **Unsupervised learning** finds patterns in unlabeled data
- **K-Means clustering** groups data into `k` clusters based on distance to centroids
- The **elbow method** helps determine the optimal number of clusters
- **Feature scaling** is essential for distance-based algorithms
- **PCA** reduces dimensionality for visualization and simplification
- Real ML projects combine: data collection → preprocessing → modeling → evaluation → insights

Congratulations — you've completed the Machine Learning path! You now have a solid foundation in NumPy, data preprocessing, supervised learning, and unsupervised learning.
