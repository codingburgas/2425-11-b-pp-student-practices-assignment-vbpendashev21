import os
import numpy as np

class TinyOutfitNet:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'trained_outfit_weights.npz')
        data = np.load(path, allow_pickle=True)
        self.weights = data['weights']
        self.biases = data['biases']
        self.outfits = list(data['outfits'])

    def _encode(self, temperature, condition):
        is_rain = 1 if condition == "rain" else 0
        is_snow = 1 if condition == "snow" else 0
        return np.array([temperature, is_rain, is_snow])

    def predict(self, temperature, condition):
        x = self._encode(temperature, condition)
        scores = np.dot(self.weights, x) + self.biases
        idx = int(np.argmax(scores))
        exp_scores = np.exp(scores - np.max(scores))
        probs = exp_scores / exp_scores.sum()
        confidence = float(probs[idx])
        return self.outfits[idx], [confidence]
