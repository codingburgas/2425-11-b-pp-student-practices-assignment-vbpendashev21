import numpy as np
import csv

# 1. Load data and find all unique outfits
data_file = 'training_data.csv'
X = []
y = []
outfit_set = set()

# First pass: collect all unique outfits
with open(data_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        outfit_set.add(row['outfit'])

# Build mappings
outfit_list = sorted(outfit_set)
outfit_to_idx = {outfit: idx for idx, outfit in enumerate(outfit_list)}
idx_to_outfit = {idx: outfit for idx, outfit in outfit_to_idx.items()}

def encode_condition(condition):
    # "sunny"=0, "rain"=1, "snow"=2
    if condition == "rain":
        return [1, 0]
    elif condition == "snow":
        return [0, 1]
    else:
        return [0, 0]

# Second pass: build features/labels arrays
with open(data_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        temp = float(row['temperature'])
        cond = encode_condition(row['condition'])
        outfit_idx = outfit_to_idx[row['outfit']]
        X.append([temp] + cond)
        y.append(outfit_idx)

X = np.array(X)
y = np.array(y)

# 2. Training a simple neural net (single layer, softmax)
np.random.seed(0)
n_classes = len(outfit_list)
n_features = X.shape[1]
weights = np.random.randn(n_classes, n_features) * 0.01
biases = np.zeros(n_classes)

# One-hot labels
y_onehot = np.zeros((y.size, n_classes))
y_onehot[np.arange(y.size), y] = 1

lr = 0.05
for epoch in range(500):  # More epochs for bigger data!
    # Forward
    logits = X @ weights.T + biases  # shape: [samples, classes]
    exps = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs = exps / exps.sum(axis=1, keepdims=True)

    # Loss (cross-entropy)
    loss = -np.sum(y_onehot * np.log(probs + 1e-8)) / X.shape[0]

    # Backward
    grad_logits = (probs - y_onehot) / X.shape[0]
    grad_weights = grad_logits.T @ X
    grad_biases = grad_logits.sum(axis=0)

    weights -= lr * grad_weights
    biases -= lr * grad_biases

    if epoch % 50 == 0:
        acc = (np.argmax(probs, axis=1) == y).mean()
        print(f"Epoch {epoch}, loss={loss:.3f}, acc={acc:.2f}")

# 3. Save weights, biases, and all possible outfits
np.savez('trained_outfit_weights.npz', weights=weights, biases=biases, outfits=outfit_list)
print("Training complete! Weights saved to trained_outfit_weights.npz")
