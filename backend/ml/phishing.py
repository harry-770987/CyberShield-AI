import os
import re
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../saved_models")

class PhishingDetector:
    def __init__(self):
        self.url_lr = None
        self.tfidf = None
        self.text_lr = None
        self.scaler = None
        self.is_loaded = False
        
    def load(self):
        try:
            self.url_lr = joblib.load(os.path.join(MODEL_DIR, "phishing_url_lr.pkl"))
            self.tfidf = joblib.load(os.path.join(MODEL_DIR, "phishing_tfidf.pkl"))
            self.text_lr = joblib.load(os.path.join(MODEL_DIR, "phishing_text_lr.pkl"))
            self.scaler = joblib.load(os.path.join(MODEL_DIR, "phishing_url_scaler.pkl"))
            self.is_loaded = True
        except Exception as e:
            print(f"PhishingDetector failed to load: {e}")

    def extract_url_features(self, url: str) -> np.ndarray:
        domain_part = url.split('/')[2] if len(url.split('/')) > 2 else url
        has_ip = 1 if re.search(r'\d+\.\d+\.\d+\.\d+', url) else 0
        suspicious_words = ['login', 'verify', 'update', 'secure', 'account', 'free', 'bonus']
        
        features = [
            len(url),                          # url_length
            url.count('.'),                    # num_dots
            url.count('-'),                    # num_hyphens
            url.count('@'),                    # num_at
            len(re.findall(r'\d', url)),       # num_digits
            has_ip,                            # has_ip
            1 if url.startswith('https') else 0, # is_https
            domain_part.count('.') - 1 if not has_ip else 0, # subdomain_count
            sum(1 for w in suspicious_words if w in url.lower()), # suspicious_words_count
            len(domain_part)                   # domain_length
        ]
        return np.array(features).reshape(1, -1)

    def predict(self, url: str, email_body: str = "") -> dict:
        if not self.is_loaded:
            return {"error": "Models not loaded"}
            
        url_feats = self.extract_url_features(url)
        url_feats_scaled = self.scaler.transform(url_feats)
        
        url_score = self.url_lr.predict_proba(url_feats_scaled)[0][1]
        
        text_score = 0.0
        if email_body and email_body.strip() != "":
            X_text = self.tfidf.transform([email_body])
            text_score = self.text_lr.predict_proba(X_text)[0][1]
            weight = (0.55, 0.45)
        else:
            weight = (1.0, 0.0)
            
        threat_score = weight[0] * url_score + weight[1] * text_score
        
        indicators = []
        if url_feats[0][5] == 1: indicators.append("IP Address in URL")
        if url_feats[0][6] == 0: indicators.append("Non-HTTPS connection")
        if url_feats[0][8] > 0: indicators.append("Suspicious keywords in URL found")
        if text_score > 0.6: indicators.append("Language model detected urgency/phishing tone in context")
        
        return {
            "threat_score": float(threat_score),
            "url_score": float(url_score),
            "text_score": float(text_score),
            "label": "phishing" if threat_score > 0.5 else "legitimate",
            "url_features": {
                "length": int(url_feats[0][0]),
                "dots": int(url_feats[0][1]),
                "https": bool(url_feats[0][6])
            },
            "suspicious_indicators": indicators
        }
        
phishing_detector = PhishingDetector()
