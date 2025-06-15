from app.simple_model import SimpleOutfitClassifier

# Sample training data
X = {
    "temperature": [0, 5, 10, 15, 20, 25],
    "condition": ["snow", "rain", "rain", "sunny", "sunny", "sunny"]
}
Y = [
    "Winter coat",
    "Raincoat",
    "Jacket + Hoodie",
    "T-shirt + Jeans",
    "T-shirt + Jeans",
    "Shorts + T-shirt"
]

model = SimpleOutfitClassifier()
model.train(X, Y, epochs=1000)
model.save()
print("✅ model_weights.json saved.")
