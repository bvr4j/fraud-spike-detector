import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies():
    # Load processed features
    df = pd.read_csv("data/processed_features.csv")
    
    # We only use failure_velocity for detection
    X = df[['failure_velocity']]
    
    # Initialize and fit the Isolation Forest model
    clf = IsolationForest(contamination=0.05, random_state=42)
    
    # Predict anomalies: -1 for anomalies, 1 for normal data points
    df['anomaly'] = clf.fit_predict(X)
    
    # Filter the anomalous data points
    anomalous_data = df[df['anomaly'] == -1]
    
    # Extract unique anomalous IP addresses
    flagged_ips = anomalous_data['ip_address'].unique().tolist()
    
    print(f"Isolation Forest detected {len(flagged_ips)} anomalous IP addresses based on failure velocity.")
    
    return flagged_ips

if __name__ == "__main__":
    detect_anomalies()
