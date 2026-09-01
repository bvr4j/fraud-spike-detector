## 🛡️ Fraud Spike Detector

An autonomous, defense-only machine learning pipeline designed to detect high-velocity card-testing attacks in real-time without blocking legitimate traffic spikes.

## 📌 Project Overview

In the digital payments ecosystem, fraudsters often use automated bots to rapidly test thousands of stolen credit card numbers. This project acts as an **"abuse-ring sentinel."** Instead of evaluating single transactions in isolation, it monitors the velocity and volume of payment events. It successfully isolates malicious card-testing attacks while accurately allowing legitimate high-volume events (like Flash Sales) to pass through seamlessly.
Crucially, this project goes beyond simple anomaly detection by implementing an **Honest False-Positive Cost** calculator. It balances security with revenue retention by mathematically measuring the simulated financial loss of accidentally blocking a legitimate customer.

## 🏗️ Architecture

This project is built using a decoupled, four-layer architecture:

1. **Data Ingestion (Simulator)**: Generates a synthetic stream of Razorpay `payment.authorized` and `payment.failed` webhooks. It establishes a normal baseline, injects a high-velocity legitimate Flash Sale, and injects a malicious 100% failure-rate card-testing attack.
2. **Feature Engineering (Processor)**: Ingests the raw JSON stream, groups events by IP address, and applies a rolling time window to extract "failure velocity" metrics using `pandas`.
3. **Machine Learning (Detection Engine)**: Utilizes an unsupervised `scikit-learn` Isolation Forest algorithm. It establishes a mathematical baseline of normal traffic and flags anomalous deviations in real-time.
4. **Orchestration (Auto-Responder & Evaluator)**: Intercepts the anomaly flags, logs a simulated defensive firewall block, and calculates the final business metrics (Precision, Recall, and the Honest False-Positive Cost in INR).

## 📂 Folder Structure

```text
fraud-spike-detector/
│
├── data/
│   ├── raw_stream.json              # Output of simulated Razorpay webhooks
│   └── processed_features.csv       # Extracted rolling-window velocity metrics
│
├── src/
│   ├── __init__.py
│   ├── data_simulator.py            # Generates baseline, flash sales, and attacks
│   ├── feature_processor.py         # Transforms raw JSON into ML-ready time-series features
│   ├── ml_engine.py                 # Scikit-learn Isolation Forest model
│   └── auto_responder.py            # Defensive orchestrator and business impact evaluator
│
├── main.py                          # Main execution pipeline
├── requirements.txt                 # Project dependencies
└── README.md                        # Project documentation
```

## 🚀 How to Run

### 1. Install Dependencies
Ensure you have Python installed, then install the required data science libraries:
```bash
pip install -r requirements.txt
```

### 2. Execute the Pipeline

Run the main orchestrator to trigger the end-to-end data generation, machine learning detection, and evaluation process:
```bash
python main.py
```

## 📊 Evaluation & Success Metrics

This pipeline was built specifically to pass the rigorous evaluation bar of the AI Risk Manager track:
- **Strictly Defensive**: The system operates purely defensively (simulating firewall blocks and temporary bans) and contains no offensive retaliation mechanics.
- **Measured Precision & Recall**: Evaluates exact True Positives (attacks successfully caught) against the known injected malicious IPs.
- **Honest False-Positive Cost**: Calculates the simulated INR revenue lost if the model mistakenly throttles a legitimate traffic spike, demonstrating a deep understanding of e-commerce risk trade-offs.

## 🛠️ Built With

- **Python 3.x**
- **Pandas**: For data manipulation and rolling-window feature engineering.
- **Scikit-Learn**: For the Isolation Forest unsupervised anomaly detection model.