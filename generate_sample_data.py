import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of samples
num_samples = 1000

# Generate synthetic data
data = {
    'transaction_id': [f'TXN{i:05d}' for i in range(num_samples)],
    'sender_account_type': np.random.choice(['Personal', 'Business'], num_samples),
    'receiver_account_type': np.random.choice(['Personal', 'Business'], num_samples),
    'transaction_amount_usd': np.round(np.random.lognormal(mean=7, sigma=1.5, size=num_samples), 2), # Skewed distribution for amounts
    'transaction_frequency_30d': np.random.randint(1, 50, num_samples),
    'avg_daily_balance_30d': np.round(np.random.lognormal(mean=9, sigma=2, size=num_samples), 2),
    'is_international': np.random.randint(0, 2, num_samples),
    'transaction_hour': np.random.randint(0, 24, num_samples),
    'ip_country_match': np.random.randint(0, 2, num_samples),
    'num_flagged_transactions_sender_90d': np.random.randint(0, 5, num_samples)
}

df = pd.DataFrame(data)

# Introduce some "money laundering" patterns (outliers)
# These will be the anomalies that Isolation Forest should ideally pick up
num_anomalies = int(num_samples * 0.02) # 2% anomalies

# High amount, low frequency, international, no IP match, new sender
for _ in range(num_anomalies // 2):
    idx = random.randint(0, num_samples - 1)
    df.loc[idx, 'transaction_amount_usd'] = np.round(np.random.uniform(50000, 1000000), 2)
    df.loc[idx, 'transaction_frequency_30d'] = random.randint(1, 3)
    df.loc[idx, 'is_international'] = 1
    df.loc[idx, 'ip_country_match'] = 0
    df.loc[idx, 'num_flagged_transactions_sender_90d'] = 0
    # Mark as laundering for validation (not used by Isolation Forest directly)
    df.loc[idx, 'is_laundering'] = 1

# Frequent small amounts from Business to Personal, possibly international
for _ in range(num_anomalies - (num_anomalies // 2)):
    idx = random.randint(0, num_samples - 1)
    df.loc[idx, 'transaction_amount_usd'] = np.round(np.random.uniform(100, 1000), 2)
    df.loc[idx, 'transaction_frequency_30d'] = random.randint(80, 150) # High frequency
    df.loc[idx, 'sender_account_type'] = 'Business'
    df.loc[idx, 'receiver_account_type'] = 'Personal'
    df.loc[idx, 'is_international'] = np.random.choice([0, 1], p=[0.3, 0.7])
    df.loc[idx, 'avg_daily_balance_30d'] = np.round(np.random.lognormal(mean=5, sigma=1), 2) # Low balance
    df.loc[idx, 'is_laundering'] = 1

# Default is_laundering to 0 (normal)
if 'is_laundering' not in df.columns:
    df['is_laundering'] = 0
else:
    df['is_laundering'].fillna(0, inplace=True)

# Save to CSV
df.to_csv('aml_training_data.csv', index=False)

print("aml_training_data.csv created successfully with the following head:")
print(df.head())
print(f"\nTotal anomalies introduced: {df['is_laundering'].sum()}")