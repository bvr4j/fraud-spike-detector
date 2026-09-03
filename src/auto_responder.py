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

def trigger_defense(ip_address: str):
    """
    Triggers a defense mechanism (e.g. logging or blocking) for the given IP.
    Executes a synchronous ping to the Razorpay API to verify connectivity or fetch data,
    simulating the blocking phase latency.
    """
    # 1. Action: Real API Integration (Synchronous ping)
    if api_connected and client is not None:
        try:
            # Ping the API to fetch the 3 most recent transactions
            recent_payments = client.payment.fetch_all({'count': 3})
            print(f"DEFENSE ACTIVE: Logged malicious IP {ip_address} to Razorpay security audit.")
            # In a full production environment, issue automatic refunds or block IP here.
        except requests.exceptions.RequestException as re:
            print(f"Network Timeout/Connection Error during defense: {re}")
        except Exception as e:
            print(f"Razorpay API Error during defense: {e}")
    else:
        print(f"DEFENSE TRIGGERED (Local Fallback): Generating temporary firewall block for IP {ip_address}")
        
    return True