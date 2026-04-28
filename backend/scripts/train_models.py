import os
import joblib
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved_models")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def train_network_model():
    print("Training Network Intrusion Model...")
    # 5 classes: Normal, DoS, Probe, R2L, U2R. Simulated NSL-KDD.
    X, y = make_classification(n_samples=5000, n_features=41, n_informative=20, n_classes=5, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save model
    joblib.dump(model, os.path.join(MODELS_DIR, "network_model.pkl"))
    
    with open(os.path.join(RESULTS_DIR, "network_report.txt"), "w") as f:
        f.write("Network Intrusion Model Report\n")
        f.write(classification_report(y, model.predict(X)))
    print("Network Model saved successfully.\n")

def train_anomaly_model():
    print("Training Anomaly Detection Model...")
    # Simulated CICIDS2017 features
    X = np.random.randn(2000, 78) # mostly normal
    outliers = np.random.uniform(low=-4, high=4, size=(100, 78))
    X_train = np.vstack([X, outliers])
    
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_train)
    
    joblib.dump(model, os.path.join(MODELS_DIR, "anomaly_model.pkl"))
    print("Anomaly Model saved successfully.\n")

def train_email_model():
    print("Training Email Phishing Model...")
    texts = [
        "Win a free iPhone now!! Click here",
        "Meeting at 10 AM regarding project status",
        "Verify your bank account details immediately to avoid suspension",
        "Hey, are we still up for lunch?",
        "Viagra cheap pills over the counter",
        "Please review the attached invoice"
    ] * 100
    y = np.array([2, 0, 2, 0, 1, 0] * 100) # 0: Ham, 1: Spam, 2: Phishing
    
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(texts)
    
    model = MultinomialNB()
    model.fit(X, y)
    
    joblib.dump(vectorizer, os.path.join(MODELS_DIR, "email_vectorizer.pkl"))
    joblib.dump(model, os.path.join(MODELS_DIR, "email_model.pkl"))
    
    with open(os.path.join(RESULTS_DIR, "email_report.txt"), "w") as f:
        f.write("Email Model Report\n")
        f.write(classification_report(y, model.predict(X)))
    print("Email Model saved successfully.\n")

def train_url_model():
    print("Training URL Detection Model...")
    # Features: length, has_https, special_chars, subdomains, digit_ratio
    # Simulate data
    X = np.array([
        [20, 1, 0, 0, 0.0], # https://google.com
        [55, 0, 5, 2, 0.2], # http://login-update.secure-bank.com.xyz/?id=123
        [23, 1, 0, 0, 0.0], # https://twitter.com
        [80, 0, 8, 3, 0.3], # ...
    ] * 500)
    y = np.array([0, 1, 0, 1] * 500)
    
    model = LogisticRegression()
    model.fit(X, y)
    
    joblib.dump(model, os.path.join(MODELS_DIR, "url_model.pkl"))
    print("URL Model saved successfully.\n")

if __name__ == "__main__":
    train_network_model()
    train_anomaly_model()
    train_email_model()
    train_url_model()
    print("All models successfully trained and saved!")
