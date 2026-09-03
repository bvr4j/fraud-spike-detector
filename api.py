from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
from collections import deque
from datetime import datetime, timedelta
import pandas as pd
from src.ml_engine import HybridMLEngine
from src.auto_responder import trigger_defense
import os

app = FastAPI(title="Fraud Spike Detector API")

# Global state for ML Engine and sliding windows
ml_engine = HybridMLEngine()
# In-memory sliding windows (deques) for quick velocity calculation
# We store tuples of (timestamp, is_failed) for each dimension
ip_window = {}
merchant_window = {}
bin_window = {}

@app.on_event("startup")
def startup_event():
    # Load historical data and train models
    if os.path.exists("data/processed_features.csv"):
        df = pd.read_csv("data/processed_features.csv")
        ml_engine.train(df)
    else:
        print("WARNING: Processed features not found. Models are NOT trained.")

def calculate_velocity(window_dict, key, current_time, is_failed, window_minutes=5):
    if key not in window_dict:
        window_dict[key] = deque()
    
    q = window_dict[key]
    
    # Remove old events outside the window
    cutoff_time = current_time - timedelta(minutes=window_minutes)
    while q and q[0][0] < cutoff_time:
        q.popleft()
        
    # Add new event
    q.append((current_time, is_failed))
    
    # Calculate velocity (sum of failed events)
    velocity = sum(1 for _, failed in q if failed)
    return velocity

@app.post("/webhook")
async def webhook(event: dict):
    # Start latency tracking
    start_time = time.perf_counter()
    
    # Parse event
    event_time = datetime.fromisoformat(event["timestamp"])
    ip = event["ip_address"]
    merchant = event["merchant_id"]
    card_bin = event["bin"]
    is_failed = 1 if event["event_type"] == "payment.failed" else 0
    
    # Update sliding windows and get features
    ip_vel = calculate_velocity(ip_window, ip, event_time, is_failed)
    merchant_vel = calculate_velocity(merchant_window, merchant, event_time, is_failed)
    bin_vel = calculate_velocity(bin_window, card_bin, event_time, is_failed)
    
    features = {
        'ip_velocity': ip_vel,
        'merchant_velocity': merchant_vel,
        'bin_velocity': bin_vel
    }
    
    action = "allowed"
    
    # Predict using Hybrid Engine
    if ml_engine.is_trained:
        is_anomaly = ml_engine.predict(features)
        
        if is_anomaly:
            # Trigger synchronous defense (including Razorpay API ping)
            trigger_defense(ip)
            action = "blocked"
            
    # Stop latency tracking
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    return {
        "status": "success",
        "action": action,
        "latency_ms": latency_ms
    }
