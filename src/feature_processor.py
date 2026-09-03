import pandas as pd

def process_features():
    # Load raw stream
    df = pd.read_json("data/raw_stream.json")
    
    # Convert timestamps to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create a boolean column for failed events
    df['is_failed'] = (df['event_type'] == 'payment.failed').astype(int)
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Create an indexed version for rolling window calculation
    df_indexed = df.set_index('timestamp')
    
    # Calculate 5-minute rolling window sum of failed events for ip_address
    ip_velocity = df_indexed.groupby('ip_address')['is_failed'].rolling('5min').sum().reset_index()
    ip_velocity.rename(columns={'is_failed': 'ip_velocity'}, inplace=True)
    
    # Calculate 5-minute rolling window sum of failed events for merchant_id
    merchant_velocity = df_indexed.groupby('merchant_id')['is_failed'].rolling('5min').sum().reset_index()
    merchant_velocity.rename(columns={'is_failed': 'merchant_velocity'}, inplace=True)
    
    # Calculate 5-minute rolling window sum of failed events for bin
    bin_velocity = df_indexed.groupby('bin')['is_failed'].rolling('5min').sum().reset_index()
    bin_velocity.rename(columns={'is_failed': 'bin_velocity'}, inplace=True)
    
    # Merge the velocity features back into the original dataframe
    # We use a sequential merge on the timestamp and respective identifier
    df = pd.merge(df, ip_velocity, on=['timestamp', 'ip_address'], how='left')
    df = pd.merge(df, merchant_velocity, on=['timestamp', 'merchant_id'], how='left')
    df = pd.merge(df, bin_velocity, on=['timestamp', 'bin'], how='left')
    
    # Save the processed features
    output_path = "data/processed_features.csv"
    df.to_csv(output_path, index=False)
    print(f"Processed features saved to {output_path}")

if __name__ == "__main__":
    process_features()
