import pandas as pd
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import os

class HybridMLEngine:
    def __init__(self):
        self.iso_forest = IsolationForest(contamination=0.05, random_state=42)
        self.xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
        self.is_trained = False
        
    def train(self, df: pd.DataFrame):
        print("Training Hybrid ML Engine...")
        # Features to use
        feature_cols = ['ip_velocity', 'merchant_velocity', 'bin_velocity']
        
        X = df[feature_cols].fillna(0) # Ensure no NaNs
        
        # 1. Train Isolation Forest (Unsupervised)
        self.iso_forest.fit(X)
        
        # 2. Train XGBoost (Supervised)
        # CRITICAL SECURITY NOTE: Prevent Data Leakage by ensuring is_fraud is NOT in X
        y = df['is_fraud']
        self.xgb_model.fit(X, y)
        
        self.is_trained = True
        print("Training complete.")

    def predict(self, features: dict) -> bool:
        """
        Takes a single event's velocity features and returns True if fraud is detected.
        features dict example: {'ip_velocity': 5, 'merchant_velocity': 100, 'bin_velocity': 50}
        """
        if not self.is_trained:
            raise RuntimeError("Models must be trained before inference.")
            
        # Create a single-row DataFrame to match expected input format
        df = pd.DataFrame([features])
        
        # Isolation Forest prediction: -1 means anomaly, 1 means normal
        iso_pred = self.iso_forest.predict(df)[0]
        iso_is_anomaly = (iso_pred == -1)
        
        # XGBoost prediction: 1 means fraud, 0 means normal
        xgb_pred = self.xgb_model.predict(df)[0]
        xgb_is_fraud = (xgb_pred == 1)
        
        # Hybrid logic: flag if *either* model detects fraud
        return iso_is_anomaly or xgb_is_fraud

def detect_anomalies():
    # Helper for batch testing, though not used by FastAPI
    if not os.path.exists("data/processed_features.csv"):
        print("No processed features found.")
        return []
        
    df = pd.read_csv("data/processed_features.csv")
    engine = HybridMLEngine()
    engine.train(df)
    
    df['anomaly'] = df.apply(lambda row: engine.predict({
        'ip_velocity': row['ip_velocity'],
        'merchant_velocity': row['merchant_velocity'],
        'bin_velocity': row['bin_velocity']
    }), axis=1)
    
    anomalous_data = df[df['anomaly'] == True]
    flagged_ips = anomalous_data['ip_address'].unique().tolist()
    
    print(f"Hybrid ML Engine detected {len(flagged_ips)} anomalous IP addresses in batch mode.")
    return flagged_ips

if __name__ == "__main__":
    detect_anomalies()
