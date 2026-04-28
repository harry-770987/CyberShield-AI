import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_log_data(num_samples: int = 20000, 
                      log_path: str = "system_logs.txt", 
                      labels_path: str = "log_labels.csv"):
    """
    Generates synthetic system logs and a corresponding labels CSV.
    5% anomalous logs.
    """
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    
    components = ['kernel', 'sshd', 'apache2', 'nginx', 'systemd', 'cron', 'sudo']
    levels = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    normal_messages = [
        "Connection closed by authenticating user root",
        "Session opened for user admin",
        "Starting cleanup of temporary directories",
        "Finished system daily tasks",
        "Serving GET request to /index.html",
        "Accepted publickey for ubuntu",
        "Reloading web server configurations",
        "Checking disk quotas"
    ]
    
    anomaly_messages = [
        "Failed password for invalid user root",
        "kernel panic - not syncing",
        "rapid process spawning detected",
        "Out of memory: Killed process 1234 (apache2)",
        "segfault at 0 ip 00007f9c8b9d3e error 4",
        "excessive connections from 192.168.1.100",
        "unauthorized access attempt to /etc/shadow"
    ]
    
    logs = []
    labels = []
    
    current_time = datetime(2024, 1, 15, 8, 0, 0)
    
    for i in range(num_samples):
        # Time progression
        is_anomaly = random.random() < 0.05
        
        if is_anomaly:
            # Anomalies might happen in rapid succession or odd hours
            current_time += timedelta(seconds=random.uniform(0.1, 5.0))
            level = random.choices(['WARNING', 'ERROR', 'CRITICAL'], weights=[0.3, 0.5, 0.2])[0]
            comp = random.choice(components)
            msg = random.choice(anomaly_messages)
            if "Failed password" in msg:
                comp = 'sshd'
        else:
            current_time += timedelta(seconds=random.uniform(10.0, 300.0))
            level = random.choices(['INFO', 'WARNING', 'ERROR', 'CRITICAL'], weights=[0.60, 0.25, 0.12, 0.03])[0]
            comp = random.choice(components)
            msg = random.choice(normal_messages)
            
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp_str} {level} {comp}: [{random.uniform(100.0, 9999.0):.4f}] {msg}"
        
        logs.append(log_line)
        labels.append({
            'line_number': i,
            'is_anomaly': 1 if is_anomaly else 0
        })
        
    # Write text logs
    with open(log_path, 'w') as f:
        for log in logs:
            f.write(log + "\n")
            
    # Write labels
    pd.DataFrame(labels).to_csv(labels_path, index=False)
    print(f"Generated {num_samples} logs at {log_path} and labels at {labels_path}")

if __name__ == "__main__":
    generate_log_data(20000, "data/system_logs.txt", "data/log_labels.csv")
