# simple_model.py
import numpy as np
import json
import os

class SimpleOutfitClassifier:
    def __init__(self):
        # Define outfit labels
        self.labels = [
            "Winter coat",
            "Jacket + Hoodie",
            "T-shirt + Jeans",
            "Shorts + T-shirt",
            "Raincoat"
        ]

        # Initialize weights and bias
        self.input_size = 5
        self.output_size = len(self.labels)
        self.weights = np.random.randn(self.input_size, self.output_size)
        self.bias = np.zeros((1, self.output_size))

    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=1, keepdims=True)

    def forward(self, X):
        logits = np.dot(X, self.weights) + self.bias
        return self.softmax(logits)

    def preprocess(self, temp, condition):
        cond_map = {
            "sunny": [1, 0, 0],
            "rain": [0, 1, 0],
            "snow": [0, 0, 1]
        }
        cond_vec = cond_map.get(condition.lower(), [0, 0, 0])
        x = np.array([[temp] + cond_vec + [1]])
        return x

    def predict(self, temp, condition):
        x = self.preprocess(temp, condition)
        probs = self.forward(x)
        pred_index = np.argmax(probs)
        return self.labels[pred_index], probs[0]

    def evaluate_batch(self, X, Y):
        correct = 0
        for i, (temp, cond, true_label) in enumerate(zip(X["temperature"], X["condition"], Y)):
            pred, _ = self.predict(temp, cond)
            if pred == true_label:
                correct += 1
        accuracy = correct / len(Y)
        return accuracy

    def train(self, X, Y, epochs=1000, lr=0.01):
        label_map = {label: i for i, label in enumerate(self.labels)}
        inputs = []
        targets = []

        for temp, cond, label in zip(X["temperature"], X["condition"], Y):
            x = self.preprocess(temp, cond)
            y = np.zeros((1, self.output_size))
            y[0, label_map[label]] = 1
            inputs.append(x[0])
            targets.append(y[0])

        inputs = np.array(inputs)
        targets = np.array(targets)

        for epoch in range(epochs):
            logits = np.dot(inputs, self.weights) + self.bias
            probs = self.softmax(logits)
            loss = -np.mean(targets * np.log(probs + 1e-9))

            grad_logits = probs - targets
            grad_weights = np.dot(inputs.T, grad_logits) / len(inputs)
            grad_bias = np.mean(grad_logits, axis=0, keepdims=True)

            self.weights -= lr * grad_weights
            self.bias -= lr * grad_bias

            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.4f}")

    def save(self, path="model_weights.json"):
        data = {
            "weights": self.weights.tolist(),
            "bias": self.bias.tolist()
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def load(self, path="model_weights.json"):
        if not os.path.exists(path):
            raise FileNotFoundError("Model weights not found.")
        with open(path, "r") as f:
            data = json.load(f)
            self.weights = np.array(data["weights"])
            self.bias = np.array(data["bias"])

    def evaluate(self, dataset):
        total = len(dataset)
        correct = 0

        for entry in dataset:
            temp = entry["temperature"]
            condition = entry["condition"]
            actual = entry["outfit"]
            predicted, _ = self.predict(temp, condition)

            if predicted.lower().strip() == actual.lower().strip():
                correct += 1

        accuracy = correct / total if total > 0 else 0
        loss = 1 - accuracy
        return accuracy, loss
