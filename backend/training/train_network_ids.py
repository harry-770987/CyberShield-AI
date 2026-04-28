import os
import json
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
import shap

# Settings
DATA_PATH = "../data/network_traffic.csv"
MODEL_DIR = "../saved_models"
REPORTS_DIR = "../reports"
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

class NetworkAutoencoder(nn.Module):
    def __init__(self, input_dim):
        super(NetworkAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16)
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim)
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def train():
    # Step 1 - Load Data
    print("Loading network traffic data...")
    df = pd.read_csv(DATA_PATH)
    print(f"Shape: {df.shape}")
    print("Class distribution:\n", df['label'].value_counts())
    
    # Step 2 - Preprocessing
    print("Preprocessing data...")
    categorical_cols = ['protocol_type', 'service', 'flag']
    numeric_cols = [c for c in df.columns if c not in categorical_cols and c != 'label']
    
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        
    X = df.drop('label', axis=1)
    y = df['label'].apply(lambda x: 1 if x == 'attack' else 0).values
    
    scaler = StandardScaler()
    X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
    
    # Handle Class Imbalance
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)
    
    # Step 3 - Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, stratify=y_res, random_state=42)
    
    # Step 4 - Model 1: Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    y_pred = rf_model.predict(X_test)
    y_proba = rf_model.predict_proba(X_test)[:, 1]
    
    print("Evaluating Random Forest...")
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    print(f"Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}, AUC-ROC: {auc:.4f}")
    print(classification_report(y_test, y_pred))
    
    # Save Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Network IDS - Random Forest Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(os.path.join(REPORTS_DIR, 'network_ids_confusion.png'))
    plt.close()
    
    # Save ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    plt.figure(figsize=(6,5))
    plt.plot(fpr, tpr, label=f'RF (AUC = {auc:.4f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title('Network IDS - ROC Curve')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend()
    plt.savefig(os.path.join(REPORTS_DIR, 'network_ids_roc.png'))
    plt.close()
    
    # Step 5 - Model 2: Autoencoder (Anomaly fallback)
    print("Training Autoencoder on normal traffic...")
    # Filter normal traffic from original scaled data (not SMOTE)
    X_normal = X[y == 0].values
    X_norm_train, X_norm_val = train_test_split(X_normal, test_size=0.2, random_state=42)
    
    train_tensor = torch.FloatTensor(X_norm_train)
    val_tensor = torch.FloatTensor(X_norm_val)
    train_loader = DataLoader(TensorDataset(train_tensor, train_tensor), batch_size=256, shuffle=True)
    val_loader = DataLoader(TensorDataset(val_tensor, val_tensor), batch_size=256, shuffle=False)
    
    input_dim = X.shape[1]
    autoencoder = NetworkAutoencoder(input_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(autoencoder.parameters(), lr=0.001)
    
    epochs = 50
    for epoch in range(epochs):
        autoencoder.train()
        train_loss = 0
        for batch_x, _ in train_loader:
            optimizer.zero_grad()
            outputs = autoencoder(batch_x)
            loss = criterion(outputs, batch_x)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            
    autoencoder.eval()
    val_losses = []
    with torch.no_grad():
        for batch_x, _ in val_loader:
            outputs = autoencoder(batch_x)
            loss = torch.mean((outputs - batch_x)**2, dim=1)
            val_losses.extend(loss.numpy())
            
    threshold = np.mean(val_losses) + 2 * np.std(val_losses)
    print(f"Autoencoder threshold computed: {threshold}")
    
    torch.save(autoencoder.state_dict(), os.path.join(MODEL_DIR, 'autoencoder_network.pt'))
    with open(os.path.join(MODEL_DIR, 'autoencoder_threshold.json'), 'w') as f:
        json.dump({'threshold': float(threshold)}, f)
        
    # Step 6 - SHAP
    print("Computing SHAP values...")
    explainer = shap.TreeExplainer(rf_model)
    X_test_sample = X_test.sample(n=min(500, len(X_test)), random_state=42)
    shap_values = explainer.shap_values(X_test_sample)
    
    # In shap 0.45, shap_values for binary RF is a list or array. Handle properly:
    vals = shap_values[1] if isinstance(shap_values, list) else shap_values[..., 1] if len(shap_values.shape) == 3 else shap_values

    plt.figure(figsize=(10,6))
    shap.summary_plot(vals, X_test_sample, show=False)
    plt.savefig(os.path.join(REPORTS_DIR, 'network_ids_shap.png'), bbox_inches='tight')
    plt.close()
    
    feature_importances = {col: float(imp) for col, imp in zip(X.columns, rf_model.feature_importances_)}
    with open(os.path.join(REPORTS_DIR, 'network_ids_features.json'), 'w') as f:
        json.dump(feature_importances, f, indent=2)
        
    # Step 7 - Save artifacts
    print("Saving models and preprocessors...")
    joblib.dump(rf_model, os.path.join(MODEL_DIR, 'network_ids_rf.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'network_ids_scaler.pkl'))
    joblib.dump(label_encoders, os.path.join(MODEL_DIR, 'network_ids_encoders.pkl'))
    print("Network IDS training complete.")

if __name__ == "__main__":
    # Change cwd relative to script to find data
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    train()
