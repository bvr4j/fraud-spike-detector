from src.data_simulator import generate_synthetic_data
from src.feature_processor import process_features
from src.ml_engine import detect_anomalies
from src.auto_responder import orchestrate_defense_and_evaluate
def main():
    print("===========================================")
    print("  Velocity-Based Fraud Spike Detector      ")
    print("===========================================")
    
    print("\n[Step 1] Generating synthetic data...")
    generate_synthetic_data()
    
    print("\n[Step 2] Processing features...")
    process_features()
    
    print("\n[Step 3] Detecting anomalies using Machine Learning...")
    flagged_ips = detect_anomalies()
    
    print("\n[Step 4] Evaluating defensive response...")
    orchestrate_defense_and_evaluate(flagged_ips)    
    print("\nPipeline execution complete.")

if __name__ == "__main__":
    main()
