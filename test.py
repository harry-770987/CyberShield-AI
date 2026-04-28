import joblib
import sys

print("Loading models...")
try:
    model = joblib.load('backend/saved_models/email_model.pkl')
    vec = joblib.load('backend/saved_models/email_vectorizer.pkl')
    print("Models loaded successfully.")
    
    text = "harshal@gmail.com"
    feats = vec.transform([text])
    print(f"Features transformed: {feats.shape}")
    
    if hasattr(model, "predict_proba"):
        probas = model.predict_proba(feats)
        print(f"Probas: {probas}")
    else:
        res = model.predict(feats)
        print(f"Prediction: {res}")
        
except Exception as e:
    print(f"Error: {e}")
