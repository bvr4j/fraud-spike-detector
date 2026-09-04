from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
from collections import deque
from datetime import datetime, timedelta
import pandas as pd
from src.ml_engine import HybridMLEngine
from src.auto_responder import generate_threat_report, trigger_defense
import os

# Set SHADOW_MODE = False for final evaluation as requested by user
SHADOW_MODE = False

app = FastAPI(title="Fraud Spike Detector API")

# Global state for ML Engine and sliding windows
ml_engine = HybridMLEngine()
ip_window = {}
merchant_window = {}
bin_window = {}

@app.on_event("startup")
def startup_event():
    mode_status = "ACTIVE (Live defense bypassed)" if SHADOW_MODE else "DISABLED (Live defense active)"
    print(f"\n[Config] Shadow Mode is {mode_status}")
    
    if os.path.exists("data/processed_features.csv"):
        df = pd.read_csv("data/processed_features.csv")
        ml_engine.train(df)
    else:
        print("WARNING: Processed features not found. Models are NOT trained.")

def calculate_velocity(window_dict, key, current_time, is_failed, window_minutes=5):
    if key not in window_dict:
        window_dict[key] = deque()
    
    q = window_dict[key]
    
    cutoff_time = current_time - timedelta(minutes=window_minutes)
    while q and q[0][0] < cutoff_time:
        q.popleft()
        
    q.append((current_time, is_failed))
    
    velocity = sum(1 for _, failed in q if failed)
    return velocity

@app.post("/webhook")
async def webhook(event: dict):
    start_time = time.perf_counter()
    
    event_time = datetime.fromisoformat(event["timestamp"])
    ip = event["ip_address"]
    merchant = event["merchant_id"]
    card_bin = event["bin"]
    is_failed = 1 if event["event_type"] == "payment.failed" else 0
    
    ip_vel = calculate_velocity(ip_window, ip, event_time, is_failed)
    merchant_vel = calculate_velocity(merchant_window, merchant, event_time, is_failed)
    bin_vel = calculate_velocity(bin_window, card_bin, event_time, is_failed)
    
    features = {
        'ip_velocity': ip_vel,
        'merchant_velocity': merchant_vel,
        'bin_velocity': bin_vel
    }
    
    action = "allowed"
    
    if ml_engine.is_trained:
        is_anomaly = ml_engine.predict(features)
        
        if is_anomaly:
            action = "3ds_challenge"
            
            # Print GenAI Threat Report regardless of Shadow Mode
            report = generate_threat_report(ip, merchant, card_bin)
            print(report)
            
            # Only trigger real API defense if Shadow Mode is disabled
            if not SHADOW_MODE:
                trigger_defense(ip, merchant, card_bin)
            
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    return {
        "status": "success",
        "action": action,
        "shadow_mode": SHADOW_MODE,
        "latency_ms": latency_ms
    }
