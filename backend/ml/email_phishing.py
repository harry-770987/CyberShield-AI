import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models", "email_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models", "email_vectorizer.pkl")

_model = None
_vectorizer = None

def load_model():
    global _model, _vectorizer
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)

def is_loaded():
    return _model is not None and _vectorizer is not None

def predict(text):
    if not is_loaded():
        return {"label": "Error", "confidence": 0.0}
        
    features_array = _vectorizer.transform([text])
    
    if hasattr(_model, "predict_proba"):
        probas = _model.predict_proba(features_array)[0]
        confidence = float(max(probas))
        class_idx = probas.argmax()
    else:
        confidence = 1.0
        class_idx = _model.predict(features_array)[0]
        
    classes = ["Ham", "Spam", "Phishing"]
    label = classes[class_idx] if class_idx < len(classes) else "Unknown"
    
    return {
        "label": label,
        "confidence": confidence
    }
