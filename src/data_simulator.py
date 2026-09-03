import json
import random
import datetime
import os

def generate_synthetic_data():
    events = []
    
    # Start time: 3 hours ago
    current_time = datetime.datetime.now() - datetime.timedelta(hours=3)
    
    # Pools
    normal_ips = [f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}" for _ in range(100)]
    merchants = [f"M{str(i).zfill(3)}" for i in range(1, 51)]
    bins = [f"{random.randint(400000, 499999)}" for _ in range(100)]
    
    # 1. Generate normal baseline traffic over ~3 hours
    for _ in range(1000):
        current_time += datetime.timedelta(seconds=random.randint(1, 10))
        event_type = "payment.authorized" if random.random() < 0.9 else "payment.failed"
        
        events.append({
            "timestamp": current_time.isoformat(),
            "ip_address": random.choice(normal_ips),
            "merchant_id": random.choice(merchants),
            "bin": random.choice(bins),
            "event_type": event_type,
            "is_fraud": 0
        })
        
    # 2. INJECT A FLASH SALE (Legitimate Traffic Spike)
    # Massive surge in traffic from a specific corporate IP or proxy, but with a normal 90% success rate.
    flash_sale_ip = "192.168.100.50"
    flash_sale_merchant = "M042"
    flash_sale_time = current_time + datetime.timedelta(minutes=5)
    
    for _ in range(300):
        flash_sale_time += datetime.timedelta(milliseconds=random.randint(100, 500))
        event_type = "payment.authorized" if random.random() < 0.9 else "payment.failed"
        
        events.append({
            "timestamp": flash_sale_time.isoformat(),
            "ip_address": flash_sale_ip,
            "merchant_id": flash_sale_merchant,
            "bin": random.choice(bins),
            "event_type": event_type,
            "is_fraud": 0
        })
        
    # 3. Inject a card-testing attack (Malicious Spike - IP Rotation)
    # Massive sudden burst of 100% payment.failed events using different IPs but targeting the same merchant and BIN.
    attack_merchant = "M099"
    attack_bin = "411111"
    attack_time = flash_sale_time + datetime.timedelta(minutes=10) 
    
    # Generate 500 unique IPs
    attack_ips = list(set([f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}" for _ in range(600)]))[:500]
    
    for ip in attack_ips:
        attack_time += datetime.timedelta(milliseconds=random.randint(10, 100))
        
        events.append({
            "timestamp": attack_time.isoformat(),
            "ip_address": ip,
            "merchant_id": attack_merchant,
            "bin": attack_bin,
            "event_type": "payment.failed",
            "is_fraud": 1
        })
        
    # Sort events chronologically to ensure the stream is in order
    events.sort(key=lambda x: x["timestamp"])
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    output_path = os.path.join("data", "raw_stream.json")
    with open(output_path, "w") as f:
        json.dump(events, f, indent=4)
        
    print(f"Synthetic dataset with {len(events)} events successfully saved to {output_path}")

if __name__ == "__main__":
    generate_synthetic_data()