import joblib
import os
import re
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models", "url_model.pkl")

_model = None

def load_model():
    global _model
    if os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)

def is_loaded():
    return _model is not None

def extract_features(url):
    length = len(url)
    has_https = 1 if "https://" in url else 0
    special_chars = len(re.findall(r'[@?!=_#%&*]', url))
    subdomains = len(url.split('.')) - 2 if len(url.split('.')) > 2 else 0
    digits = len(re.findall(r'\d', url))
    digit_ratio = digits / length if length > 0 else 0
    return [length, has_https, special_chars, subdomains, digit_ratio]

def predict(url):
    if not is_loaded():
        return {"label": "Error", "confidence": 0.0}
        
    features = extract_features(url)
    features_array = np.array(features).reshape(1, -1)
    
    if hasattr(_model, "predict_proba"):
        probas = _model.predict_proba(features_array)[0]
        confidence = float(max(probas))
        class_idx = probas.argmax()
    else:
        confidence = 1.0
        class_idx = _model.predict(features_array)[0]
        
    classes = ["Normal", "Suspicious"]
    label = classes[class_idx] if class_idx < len(classes) else "Unknown"
    
    return {
        "label": label,
        "confidence": confidence
    }
