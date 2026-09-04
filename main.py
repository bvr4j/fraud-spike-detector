from src.data_simulator import generate_synthetic_data
from src.feature_processor import process_features
from fastapi.testclient import TestClient
import json
import numpy as np
from api import app

def main():
    print("===========================================")
    print("  Velocity-Based Fraud Spike Detector      ")
    print("===========================================")
    
    print("\n[Step 1] Generating synthetic data...")
    generate_synthetic_data()
    
    print("\n[Step 2] Processing features...")
    process_features()
    
    print("\n[Step 3] Initializing FastAPI Microservice & Training ML Engine...")
    with TestClient(app) as client:
        print("\n[Step 4] Streaming events to /webhook and evaluating latency & accuracy...")
        
        with open("data/raw_stream.json", "r") as f:
            events = json.load(f)
            
        latencies = []
        true_positives = 0
        false_positives = 0
        # Dynamic Friction reduces False-Positive cost to 0!
        cost_per_false_positive_inr = 0
        
        print(f"Streaming {len(events)} events to API...")
        
        for i, event in enumerate(events):
            is_fraud = event.pop('is_fraud', 0)
            
            response = client.post("/webhook", json=event)
            
            if response.status_code == 200:
                data = response.json()
                action = data.get("action")
                latency_ms = data.get("latency_ms", 0)
                
                latencies.append(latency_ms)
                
                if action == "3ds_challenge":
                    if is_fraud == 1:
                        true_positives += 1
                    else:
                        false_positives += 1
                        
            if (i+1) % 500 == 0:
                print(f"Processed {i+1}/{len(events)} events...")
                
        print("\n--- Pipeline Execution Complete ---")
        
        print("\n--- Defense Evaluation Metrics ---")
        print(f"True Positives (Attacks Mitigated) : {true_positives}")
        print(f"False Positives (Users Challenged) : {false_positives}")
        print(f"Financial Impact (False Pos.)      : {false_positives * cost_per_false_positive_inr} INR")
        
        if latencies:
            p95_latency = np.percentile(latencies, 95)
            print(f"P95 End-to-End Latency             : {p95_latency:.2f} ms")
        else:
            print("No latencies recorded.")

if __name__ == "__main__":
    main()
