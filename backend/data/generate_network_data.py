import os
import random
import pandas as pd
import numpy as np

def generate_network_data(num_samples: int = 50000, output_path: str = "network_traffic.csv"):
    """
    Generates synthetic network traffic data simulating NSL-KDD dataset.
    70% normal traffic, 30% attack traffic.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    data = []
    protocols = ['tcp', 'udp', 'icmp']
    services = ['http', 'ftp', 'smtp', 'ssh', 'dns', 'other']
    flags = ['SF', 'S0', 'REJ', 'RSTO', 'SH']
    
    num_normal = int(num_samples * 0.7)
    num_attack = num_samples - num_normal
    
    # Generate Normal Traffic
    for _ in range(num_normal):
        data.append({
            'duration': np.random.exponential(scale=1.5),
            'protocol_type': random.choice(['tcp', 'udp']),
            'service': random.choice(['http', 'smtp', 'dns']),
            'flag': 'SF',  # Typically normal connections finish
            'src_bytes': int(np.random.normal(loc=500, scale=100)),
            'dst_bytes': int(np.random.normal(loc=1000, scale=200)),
            'land': 0,
            'wrong_fragment': 0,
            'urgent': 0,
            'hot': random.choices([0, 1], weights=[0.99, 0.01])[0],
            'num_failed_logins': 0,
            'logged_in': random.choices([0, 1], weights=[0.2, 0.8])[0],
            'num_compromised': 0,
            'count': int(np.random.uniform(1, 10)),
            'srv_count': int(np.random.uniform(1, 10)),
            'serror_rate': np.random.uniform(0, 0.01),
            'rerror_rate': np.random.uniform(0, 0.01),
            'label': 'normal'
        })
        
    # Generate Attack Traffic
    for _ in range(num_attack):
        data.append({
            'duration': np.random.exponential(scale=10.0), # Attacks might hang or be instant
            'protocol_type': random.choice(protocols),
            'service': random.choice(services),
            'flag': random.choices(['S0', 'REJ', 'RSTO', 'SH'], weights=[0.4, 0.3, 0.2, 0.1])[0],
            'src_bytes': int(np.abs(np.random.normal(loc=5000, scale=2000))), # Anomalously large
            'dst_bytes': int(np.abs(np.random.normal(loc=100, scale=50))),    # Anomalously small or zero
            'land': random.choices([0, 1], weights=[0.95, 0.05])[0],
            'wrong_fragment': random.choices([0, 1, 3], weights=[0.8, 0.1, 0.1])[0],
            'urgent': random.choices([0, 1, 2], weights=[0.9, 0.05, 0.05])[0],
            'hot': random.choices([0, 1, 5, 20], weights=[0.6, 0.2, 0.1, 0.1])[0],
            'num_failed_logins': int(np.random.exponential(scale=3.0)), # Brute force signal
            'logged_in': random.choices([0, 1], weights=[0.8, 0.2])[0],
            'num_compromised': int(np.random.exponential(scale=0.5)),
            'count': int(np.random.uniform(100, 500)), # DDoS signal
            'srv_count': int(np.random.uniform(100, 500)),
            'serror_rate': np.random.uniform(0.5, 1.0),
            'rerror_rate': np.random.uniform(0.5, 1.0),
            'label': 'attack'
        })
        
    df = pd.DataFrame(data)
    
    # Ensure no negative bytes
    df['src_bytes'] = df['src_bytes'].clip(lower=0)
    df['dst_bytes'] = df['dst_bytes'].clip(lower=0)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} network traffic records at {output_path}")

if __name__ == "__main__":
    generate_network_data(50000, "data/network_traffic.csv")
