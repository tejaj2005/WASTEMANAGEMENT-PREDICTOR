import pandas as pd
from datetime import datetime
import os

LOG_FILE = "detection_log.csv"

def log_detection(class_name, confidence, recycling_type, reuse_suggestion):
    """
    Logs a detected E-Waste item with timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_entry = {
        "Timestamp": timestamp,
        "Object": class_name,
        "Confidence": f"{confidence:.2f}",
        "Recycling_Method": recycling_type,
        "Reuse_Suggestion": reuse_suggestion
    }
    
    # Check if file exists to determine if we need header
    file_exists = os.path.isfile(LOG_FILE)
    
    df = pd.DataFrame([new_entry])
    
    # Append to CSV
    df.to_csv(LOG_FILE, mode='a', header=not file_exists, index=False)

def get_recent_logs(limit=10):
    """
    Returns the most recent detections.
    """
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["Timestamp", "Object", "Confidence", "Recycling_Method", "Reuse_Suggestion"])
    
    try:
        df = pd.read_csv(LOG_FILE)
        return df.tail(limit).iloc[::-1] # Reverse data to show newest first
    except Exception:
        return pd.DataFrame()
