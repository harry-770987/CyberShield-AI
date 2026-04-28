import joblib
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models", "anomaly_model.pkl")

_model = None

def load_model():
    global _model
    if os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)

def is_loaded():
    return _model is not None

def predict(features):
    if not is_loaded():
        return {"score": 0.0, "label": "Model Not Loaded"}
        
    features_array = np.array(features).reshape(1, -1)
    
    # Isolation forest
    score = _model.score_samples(features_array)[0]
    # score is usually negative. More negative = more anomalous. Let's normalize it to 0-1 for API consistency roughly
    # Alternatively, 1 for normal, -1 for anomaly is the `predict` return.
    prediction = _model.predict(features_array)[0]
    
    label = "Normal" if prediction == 1 else "Suspicious"
    
    # Convert score to a pseudo-confidence [0, 1] - Isolation forest scores are typically negative
    normalized_score = float(abs(score)) 
    
    return {
        "score": normalized_score,
        "label": label
    }
