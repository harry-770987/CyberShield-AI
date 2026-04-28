from .network_ids import network_ids
from .log_anomaly import log_anomaly
from .phishing import phishing_detector
from .malware import malware_detector

def load_all_models():
    print("Initializing CyberShield Machine Learning Engine Data...")
    try:
        network_ids.load()
        print("Network IDS Model Loaded.")
    except Exception as e:
         print(f"Network error: {e}")
         
    try:
        log_anomaly.load()
        print("Log Anomaly Model Loaded.")
    except Exception as e:
         print(f"Log error: {e}")
         
    try:
        phishing_detector.load()
        print("Phishing URL Model Loaded.")
    except Exception as e:
         print(f"Phishing error: {e}")
         
    try:
        malware_detector.load()
        print("Malware Static & CNN Model Loaded.")
    except Exception as e:
         print(f"Malware error: {e}")
         
    print("Machine Learning Models Ready.")
    
def get_loaded_status():
    return {
        "network_ids": network_ids.is_loaded,
        "log_anomaly": log_anomaly.is_loaded,
        "phishing": phishing_detector.is_loaded,
        "malware": malware_detector.is_loaded
    }
