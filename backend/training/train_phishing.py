import os
import json
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import shap

DATA_PATH = "../data/phishing_data.csv"
MODEL_DIR = "../saved_models"
REPORTS_DIR = "../reports"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def train():
    # Step 1 - Load phishing_data.csv
    print("Loading phishing data...")
    df = pd.read_csv(DATA_PATH)
    
    # Step 2 - URL feature model (Logistic Regression)
    print("Training URL feature model...")
    url_feature_cols = [
        'url_length', 'num_dots', 'num_hyphens', 'num_at', 'num_digits',
        'has_ip', 'is_https', 'subdomain_count', 'suspicious_words_count', 'domain_length'
    ]
    
    X_url = df[url_feature_cols].values
    y = df['label'].values
    
    scaler = StandardScaler()
    X_url_scaled = scaler.fit_transform(X_url)
    
    X_train_u, X_test_u, y_train, y_test = train_test_split(X_url_scaled, y, test_size=0.2, random_state=42)
    
    url_lr = LogisticRegression(C=1.0, max_iter=1000, class_weight='balanced', random_state=42)
    url_lr.fit(X_train_u, y_train)
    
    y_pred_u = url_lr.predict(X_test_u)
    y_proba_u = url_lr.predict_proba(X_test_u)[:, 1]
    
    print(f"URL LR Accuracy: {accuracy_score(y_test, y_pred_u):.4f}")
    print(f"URL LR F1: {f1_score(y_test, y_pred_u):.4f}")
    print(f"URL LR AUC-ROC: {roc_auc_score(y_test, y_proba_u):.4f}")
    
    joblib.dump(url_lr, os.path.join(MODEL_DIR, 'phishing_url_lr.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'phishing_url_scaler.pkl'))
    
    # Step 3 - Text model (TF-IDF + Logistic Regression)
    print("Training Text model...")
    texts = df['email_body'].fillna("").values
    
    tfidf = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1,2),
        stop_words='english',
        sublinear_tf=True
    )
    X_text = tfidf.fit_transform(texts)
    
    X_train_t, X_test_t, _, _ = train_test_split(X_text, y, test_size=0.2, random_state=42)
    
    text_lr = LogisticRegression(C=0.5, max_iter=500, random_state=42)
    text_lr.fit(X_train_t, y_train)
    
    y_pred_t = text_lr.predict(X_test_t)
    y_proba_t = text_lr.predict_proba(X_test_t)[:, 1]
    
    print(f"Text LR Accuracy: {accuracy_score(y_test, y_pred_t):.4f}")
    print(f"Text LR F1: {f1_score(y_test, y_pred_t):.4f}")
    print(f"Text LR AUC-ROC: {roc_auc_score(y_test, y_proba_t):.4f}")
    
    joblib.dump(tfidf, os.path.join(MODEL_DIR, 'phishing_tfidf.pkl'))
    joblib.dump(text_lr, os.path.join(MODEL_DIR, 'phishing_text_lr.pkl'))
    
    # Step 4 - Ensemble combination
    print("Evaluating Ensemble combination...")
    combined_proba = 0.55 * y_proba_u + 0.45 * y_proba_t
    y_pred_comb = (combined_proba > 0.5).astype(int)
    
    print(f"Combined Ensemble Accuracy: {accuracy_score(y_test, y_pred_comb):.4f}")
    print(f"Combined Ensemble F1: {f1_score(y_test, y_pred_comb):.4f}")
    
    # Step 5 - SHAP for URL LR model
    print("Computing SHAP for URL model...")
    explainer = shap.LinearExplainer(url_lr, X_train_u)
    # Extract coefficients as importance
    feature_importance = {col: float(coef) for col, coef in zip(url_feature_cols, url_lr.coef_[0])}
    
    with open(os.path.join(REPORTS_DIR, 'phishing_features.json'), 'w') as f:
        json.dump(feature_importance, f, indent=2)
        
    print("Phishing training complete.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    train()
