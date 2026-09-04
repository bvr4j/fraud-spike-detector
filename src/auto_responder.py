import os
import razorpay
import requests
from dotenv import load_dotenv

# Load the secret keys from the .env file
load_dotenv()

# Global initialization to simulate a production connection pool
api_connected = False
client = None

try:
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    if key_id and key_secret:
        client = razorpay.Client(auth=(key_id, key_secret))
        api_connected = True
except Exception as e:
    print(f"Error initializing Razorpay client: {e}")

def generate_threat_report(ip: str, merchant_id: str, bin: str) -> str:
    """
    Simulates a GenAI explainability layer that diagnoses the anomaly.
    """
    return f"[GenAI Analyst]: High-velocity anomaly detected. IP {ip} is testing BIN {bin} at Merchant {merchant_id}. Recommended Action: Step-up authentication (3D-Secure)."

def trigger_defense(ip_address: str, merchant_id: str, bin: str):
    """
    Triggers the 3D-Secure dynamic friction defense mechanism.
    Executes a synchronous ping to the Razorpay API to verify connectivity or fetch data,
    simulating the blocking phase latency.
    """
    if api_connected and client is not None:
        try:
            # Ping the API to fetch the 3 most recent transactions
            recent_payments = client.payment.fetch_all({'count': 3})
            print(f"DEFENSE ACTIVE: Triggering 3D-Secure OTP Challenge for IP {ip_address} on BIN {bin}.")
        except requests.exceptions.RequestException as re:
            print(f"Network Timeout/Connection Error during defense: {re}")
        except Exception as e:
            print(f"Razorpay API Error during defense: {e}")
    else:
        print(f"DEFENSE TRIGGERED (Local Fallback): Triggering 3D-Secure OTP Challenge for IP {ip_address} on BIN {bin}.")
        
    return True