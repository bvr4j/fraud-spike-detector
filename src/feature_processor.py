import pandas as pd

def process_features():
    # Load raw stream
    df = pd.read_json("data/raw_stream.json")
    
    # Convert timestamps to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create a boolean column for failed events
    df['is_failed'] = (df['event_type'] == 'payment.failed').astype(int)
    
    # Sort by timestamp and set as index for rolling window calculation
    df = df.sort_values('timestamp').set_index('timestamp')
    
    # Group by IP address and calculate 5-minute rolling window sum of failed events
    feature_df = df.groupby('ip_address')['is_failed'].rolling('5min').sum().reset_index()
    
    # Rename the column to represent our failure velocity metric
    feature_df.rename(columns={'is_failed': 'failure_velocity'}, inplace=True)
    
    # Save the processed features
    output_path = "data/processed_features.csv"
    feature_df.to_csv(output_path, index=False)
    print(f"Processed features saved to {output_path}")

if __name__ == "__main__":
    process_features()
