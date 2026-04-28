import os
import re
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score

DATA_DIR = "../data"
LOG_FILE = os.path.join(DATA_DIR, "system_logs.txt")
LABEL_FILE = os.path.join(DATA_DIR, "log_labels.csv")
MODEL_DIR = "../saved_models"

os.makedirs(MODEL_DIR, exist_ok=True)

class LogLSTM(nn.Module):
    def __init__(self, input_size):
        super(LogLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=64, num_layers=2, batch_first=True, dropout=0.3)
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :] # Take last sequence output
        out = self.fc(out)
        return out

def parse_logs():
    pattern = re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<component>\w+): \[(?P<pid>\d+\.\d+)\] (?P<message>.*)$")
    
    data = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                data.append(match.groupdict())
                
    return pd.DataFrame(data)

def extract_features(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    df['message_length'] = df['message'].apply(len)
    df['contains_error_keyword'] = df['message'].apply(lambda x: 1 if any(w in x.lower() for w in ['fail', 'error', 'panic', 'killed', 'segfault', 'unauthorized']) else 0)
    df['contains_ip_address'] = df['message'].apply(lambda x: 1 if re.search(r'\d+\.\d+\.\d+\.\d+', x) else 0)
    df['contains_port_number'] = df['message'].apply(lambda x: 1 if re.search(r'port \d+', x) else 0)
    df['failed_attempt_count'] = df['message'].apply(lambda x: x.lower().count('failed'))
    
    return df

def create_sequences(X, y, seq_length=20):
    Xs, ys = [], []
    for i in range(len(X) - seq_length):
        Xs.append(X[i:(i + seq_length)])
        ys.append(y[i + seq_length])
    return np.array(Xs), np.array(ys)

def train():
    # Step 1 - Parse log file
    print("Parsing logs...")
    df = parse_logs()
    labels = pd.read_csv(LABEL_FILE)
    
    df = extract_features(df)
    
    encoders = {}
    for col in ['level', 'component']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
        
    feature_cols = ['level', 'component', 'hour_of_day', 'minute', 'day_of_week', 
                    'message_length', 'contains_error_keyword', 'contains_ip_address', 
                    'contains_port_number', 'failed_attempt_count'] # This gives 10 cols, not 8, but matches spec instructions. Wait, spec says "Result: feature matrix of shape (num_logs, 8)" - but there are 10 specified. We will strictly use the 8 numeric/categorical features. Let's select exactly 8 features to match LSTM input_size=8.
                    
    feature_cols = ['level', 'component', 'hour_of_day', 'message_length', 
                    'contains_error_keyword', 'contains_ip_address', 
                    'contains_port_number', 'failed_attempt_count']
                    
    X = df[feature_cols].values
    y = labels['is_anomaly'].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Step 2 - Model 1: Isolation Forest
    print("Training Isolation Forest...")
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples='auto',
        random_state=42
    )
    iso_forest.fit(X_scaled)
    
    # Get scores and minmax scale
    iso_scores = -iso_forest.score_samples(X_scaled) # higher score = more anomalous
    mm_scaler = MinMaxScaler(feature_range=(0.0, 1.0))
    iso_scores_scaled = mm_scaler.fit_transform(iso_scores.reshape(-1, 1)).flatten()
    
    y_pred_iso = (iso_scores_scaled > 0.5).astype(int)
    print("Isolation Forest evaluation:")
    print(f"Precision: {precision_score(y, y_pred_iso):.4f}, Recall: {recall_score(y, y_pred_iso):.4f}, F1: {f1_score(y, y_pred_iso):.4f}")
    
    joblib.dump(iso_forest, os.path.join(MODEL_DIR, 'log_anomaly_isoforest.pkl'))
    
    # Step 3 - Model 2: LSTM Sequence Model
    print("Training LSTM Sequence Model...")
    X_seq, y_seq = create_sequences(X_scaled, y, seq_length=20)
    
    X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)
    
    train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
    test_tensor = torch.FloatTensor(X_test)
    y_test_tensor = torch.FloatTensor(y_test).unsqueeze(1)
    
    train_loader = DataLoader(TensorDataset(train_tensor, y_train_tensor), batch_size=64, shuffle=True)
    
    lstm_model = LogLSTM(input_size=8)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(lstm_model.parameters(), lr=0.001)
    
    epochs = 30
    for epoch in range(epochs):
        lstm_model.train()
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = lstm_model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
    lstm_model.eval()
    with torch.no_grad():
        test_preds = lstm_model(test_tensor)
        test_preds_binary = (test_preds.numpy() > 0.5).astype(int)
        acc = (test_preds_binary == y_test_tensor.numpy()).mean()
        print(f"LSTM Test Accuracy: {acc:.4f}")
        
    torch.save(lstm_model.state_dict(), os.path.join(MODEL_DIR, 'log_anomaly_lstm.pt'))
    
    # Step 4 - Save bounds
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'log_anomaly_scaler.pkl'))
    joblib.dump(encoders, os.path.join(MODEL_DIR, 'log_anomaly_encoders.pkl'))
    joblib.dump({'mm_scaler': mm_scaler}, os.path.join(MODEL_DIR, 'log_anomaly_mmscaler.pkl'))
    print("Log Anomaly training complete.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    train()
