import os
import re
import joblib
import pandas as pd
import numpy as np
import torch
import torch.nn as nn

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../saved_models")

class LogLSTM(nn.Module):
    def __init__(self, input_size):
        super(LogLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=64, num_layers=2, batch_first=True, dropout=0.3)
        self.fc = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1), nn.Sigmoid())
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

class LogAnomalyDetector:
    def __init__(self):
        self.isoforest = None
        self.lstm = None
        self.scaler = None
        self.encoders = None
        self.mm_scaler = None
        self.is_loaded = False
        
    def load(self):
        try:
            self.isoforest = joblib.load(os.path.join(MODEL_DIR, "log_anomaly_isoforest.pkl"))
            self.scaler = joblib.load(os.path.join(MODEL_DIR, "log_anomaly_scaler.pkl"))
            self.encoders = joblib.load(os.path.join(MODEL_DIR, "log_anomaly_encoders.pkl"))
            self.mm_scaler = joblib.load(os.path.join(MODEL_DIR, "log_anomaly_mmscaler.pkl"))['mm_scaler']
            
            self.lstm = LogLSTM(input_size=8)
            self.lstm.load_state_dict(torch.load(os.path.join(MODEL_DIR, "log_anomaly_lstm.pt")))
            self.lstm.eval()
            self.is_loaded = True
        except Exception as e:
            print(f"LogAnomalyDetector failed to load: {e}")

    def parse_logs(self, log_text: str) -> pd.DataFrame:
        pattern = re.compile(r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<component>\w+): \[(?P<pid>\d+\.\d+)\] (?P<message>.*)$")
        data = []
        lines = log_text.strip().split("\n")
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                data.append(match.groupdict())
            else:
                # Fallback for irregular logs
                data.append({
                    "timestamp": "2024-01-01 00:00:00",
                    "level": "INFO",
                    "component": "unknown",
                    "message": line.strip()
                })
        return pd.DataFrame(data), lines

    def extract_features(self, df: pd.DataFrame) -> np.ndarray:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').fillna(pd.to_datetime("2024-01-01 00:00:00"))
        df['hour_of_day'] = df['timestamp'].dt.hour
        for col in ['level', 'component']:
            try:
                df[col] = self.encoders[col].transform(df[col].astype(str))
            except:
                df[col] = 0
                
        df['message_length'] = df['message'].apply(len)
        df['contains_error_keyword'] = df['message'].apply(lambda x: 1 if any(w in x.lower() for w in ['fail', 'error', 'panic', 'killed', 'segfault', 'unauthorized']) else 0)
        df['contains_ip_address'] = df['message'].apply(lambda x: 1 if re.search(r'\d+\.\d+\.\d+\.\d+', x) else 0)
        df['contains_port_number'] = df['message'].apply(lambda x: 1 if re.search(r'port \d+', x) else 0)
        df['failed_attempt_count'] = df['message'].apply(lambda x: x.lower().count('failed'))
        
        feature_cols = ['level', 'component', 'hour_of_day', 'message_length', 
                        'contains_error_keyword', 'contains_ip_address', 
                        'contains_port_number', 'failed_attempt_count']
        
        return self.scaler.transform(df[feature_cols].values)

    def predict(self, log_text: str) -> dict:
        if not self.is_loaded:
             return {"error": "Models not loaded"}
             
        df, raw_lines = self.parse_logs(log_text)
        if len(df) == 0:
            return {"error": "No valid log sequences found."}
            
        X = self.extract_features(df)
        
        # 1. Isolation Forest
        iso_scores = -self.isoforest.score_samples(X)
        iso_scores_scaled = self.mm_scaler.transform(iso_scores.reshape(-1, 1)).flatten()
        
        # 2. LSTM (Sliding windows)
        seq_length = min(20, len(X))
        lstm_scores_scaled = np.zeros(len(X))
        
        if seq_length > 1:
            Xs = []
            for i in range(len(X) - seq_length + 1):
                Xs.append(X[i:i + seq_length])
            
            if Xs:
                with torch.no_grad():
                    lstm_out = self.lstm(torch.FloatTensor(np.array(Xs))).numpy().flatten()
                
                # Pad earlier predictions with 0s or replicate the first
                pad_len = len(X) - len(lstm_out)
                lstm_scores_scaled = np.pad(lstm_out, (pad_len, 0), mode='edge')
            
        combined_scores = 0.5 * iso_scores_scaled + 0.5 * lstm_scores_scaled
        
        anomalous_indices = np.where(combined_scores > 0.5)[0]
        flagged_entries = []
        for idx in anomalous_indices:
            flagged_entries.append({
                "line_number": int(idx + 1),
                "log_line": raw_lines[idx],
                "score": float(combined_scores[idx])
            })
            
        top_idx = np.argmax(combined_scores)
        
        return {
            "threat_score": float(np.mean(combined_scores) if len(combined_scores) > 0 else 0),
            "total_lines": len(raw_lines),
            "anomalous_lines": len(anomalous_indices),
            "anomaly_rate": float(len(anomalous_indices) / len(raw_lines)),
            "flagged_entries": flagged_entries,
            "top_anomaly": raw_lines[top_idx] if len(raw_lines)>0 else ""
        }

log_anomaly = LogAnomalyDetector()
