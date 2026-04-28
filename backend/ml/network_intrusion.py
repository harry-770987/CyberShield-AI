import joblib
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models", "network_model.pkl")

_model = None

def load_model():
    global _model
    if os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)

def is_loaded():
    return _model is not None

def predict(features):
    if not is_loaded():
        return {"label": "Error", "confidence": 0.0, "category": "Model Not Loaded"}
    
    features_array = np.array(features).reshape(1, -1)
    
    # Predict probabilities
    if hasattr(_model, "predict_proba"):
        probas = _model.predict_proba(features_array)[0]
        confidence = float(np.max(probas))
        class_idx = np.argmax(probas)
    else:
        confidence = 1.0
        class_idx = _model.predict(features_array)[0]
        
    classes = ["Normal", "DoS", "Probe", "R2L", "U2R"]
    label = classes[class_idx] if class_idx < len(classes) else "Unknown"
    category = "Network"
    
    return {
        "label": label,
        "confidence": confidence,
        "category": category
    }
