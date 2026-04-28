import os
import json
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../saved_models")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../reports")

class NetworkAutoencoder(nn.Module):
    def __init__(self, input_dim):
        super(NetworkAutoencoder, self).__init__()
        self.encoder = nn.Sequential(nn.Linear(input_dim, 64), nn.ReLU(), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 16))
        self.decoder = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 64), nn.ReLU(), nn.Linear(64, input_dim))
    def forward(self, x):
        return self.decoder(self.encoder(x))

class NetworkIDSDetector:
    def __init__(self):
        self.rf_model = None
        self.scaler = None
        self.encoders = None
        self.autoencoder = None
        self.ae_threshold = 0.0
        self.feature_importance = None
        self.is_loaded = False
        
    def load(self):
        try:
            self.rf_model = joblib.load(os.path.join(MODEL_DIR, "network_ids_rf.pkl"))
            self.scaler = joblib.load(os.path.join(MODEL_DIR, "network_ids_scaler.pkl"))
            self.encoders = joblib.load(os.path.join(MODEL_DIR, "network_ids_encoders.pkl"))
            
            # Load autoencoder structure dynamically based on scaler input dim
            input_dim = self.scaler.scale_.shape[0]
            self.autoencoder = NetworkAutoencoder(input_dim)
            self.autoencoder.load_state_dict(torch.load(os.path.join(MODEL_DIR, "autoencoder_network.pt")))
            self.autoencoder.eval()
            
            with open(os.path.join(MODEL_DIR, "autoencoder_threshold.json"), "r") as f:
                self.ae_threshold = json.load(f).get("threshold", 0.5)
                
            with open(os.path.join(REPORTS_DIR, "network_ids_features.json"), "r") as f:
                self.feature_importance = json.load(f)
                
            self.is_loaded = True
        except Exception as e:
            print(f"NetworkIDS model failed to load: {e}")

    def preprocess(self, features: dict) -> np.ndarray:
        df = pd.DataFrame([features])
        for col in ['protocol_type', 'service', 'flag']:
            if col in df and col in self.encoders:
                # Handle unknown categories gracefully using -1 or popular if needed
                try:
                    df[col] = self.encoders[col].transform(df[col].astype(str))
                except ValueError:
                    df[col] = 0 # Default to 0 index if completely unseen
        
        numeric_cols = [c for c in df.columns if c not in ['protocol_type', 'service', 'flag', 'label']]
        df[numeric_cols] = self.scaler.transform(df[numeric_cols])
        return df.values

    def predict(self, features: dict) -> dict:
        if not self.is_loaded:
            return {"error": "Models not loaded"}
            
        try:
            X = self.preprocess(features)
            
            rf_proba = self.rf_model.predict_proba(X)[0][1]
            
            x_tensor = torch.FloatTensor(X)
            with torch.no_grad():
                reconstructed = self.autoencoder(x_tensor)
                mse = torch.mean((reconstructed - x_tensor)**2).item()
                
            # Normalize ae score over threshold, capped at 1.0
            autoencoder_score = min(mse / (self.ae_threshold * 2), 1.0)
            
            threat_score = 0.7 * rf_proba + 0.3 * autoencoder_score
            predicted_class = "attack" if threat_score > 0.5 else "normal"
            
            top_features = [{"feature": k, "importance": v} for k, v in list(self.feature_importance.items())[:10]]
            
            return {
                "threat_score": float(threat_score),
                "rf_confidence": float(rf_proba),
                "autoencoder_score": float(autoencoder_score),
                "predicted_class": predicted_class,
                "top_features": top_features,
                "shap_explanation": {"impact": "SHAP static precomputed for speed"}
            }
        except Exception as e:
            return {"error": str(e)}

network_ids = NetworkIDSDetector()
