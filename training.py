import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib # For saving/loading the model and preprocessor

# Load the generated training data
try:
    df = pd.read_csv('aml_training_data.csv')
    print("Data loaded successfully.")
except FileNotFoundError:
    print("Error: aml_training_data.csv not found. Please run the data generation script first.")
    exit()

# Define numerical and categorical features
numerical_features = [
    'transaction_amount_usd', 'transaction_frequency_30d',
    'avg_daily_balance_30d', 'transaction_hour',
    'num_flagged_transactions_sender_90d'
]
categorical_features = [
    'sender_account_type', 'receiver_account_type',
    'is_international', 'ip_country_match'
]

# Create a preprocessor using ColumnTransformer for one-hot encoding categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough' # Keep other columns (like transaction_id if present in X)
)

# Fit the preprocessor on the training data
# We'll use all features except 'transaction_id' and 'is_laundering' for training the model
features_for_training = numerical_features + categorical_features
X_train = df[features_for_training]
preprocessor.fit(X_train)

# Transform the training data
X_train_processed = preprocessor.transform(X_train)
print(f"Shape of processed training data: {X_train_processed.shape}")

# Initialize Isolation Forest model
# contamination: The proportion of outliers in the dataset.
# This is an important parameter; setting it close to the actual proportion of anomalies
# in your training data can help, but it's often a hyperparameter to tune.
# For unsupervised anomaly detection, a common practice is to estimate it (e.g., 0.01 to 0.05).
model = IsolationForest(
    n_estimators=100,      # Number of base estimators (trees)
    max_samples='auto',    # Number of samples to draw from X to train each base estimator
    contamination=0.02,    # Expected proportion of outliers in the data
    random_state=42,       # For reproducibility
    n_jobs=-1              # Use all available CPU cores
)

# Train the model
# Isolation Forest is typically trained on a dataset assumed to be mostly "normal"
model.fit(X_train_processed)
print("Isolation Forest model trained successfully.")

# Save the trained model and preprocessor
joblib.dump(model, 'aml_isolation_forest_model.pkl')
joblib.dump(preprocessor, 'aml_preprocessor.pkl')

print("Model and preprocessor saved as 'aml_isolation_forest_model.pkl' and 'aml_preprocessor.pkl'")

# Optional: Evaluate the model on training data (for understanding, not strict performance)
df['anomaly_score'] = model.decision_function(X_train_processed)
df['is_anomaly_predicted'] = model.predict(X_train_processed)
# IsolationForest.predict() returns 1 for inliers and -1 for outliers
# Let's map it to 0 for normal, 1 for anomaly
df['is_anomaly_predicted'] = df['is_anomaly_predicted'].map({1: 0, -1: 1})

print("\nSample predictions on training data:")
print(df[['transaction_id', 'transaction_amount_usd', 'transaction_frequency_30d', 'is_laundering', 'anomaly_score', 'is_anomaly_predicted']].head(10))

# Print some actual anomalies detected
print("\nSome true anomalies and their predicted status:")
print(df[df['is_laundering'] == 1][['transaction_id', 'transaction_amount_usd', 'is_laundering', 'anomaly_score', 'is_anomaly_predicted']].head(10))

# Print some high-score anomalies (model's confidence in anomaly)
print("\nTop 5 predicted anomalies (lowest anomaly score):")
print(df.sort_values(by='anomaly_score', ascending=True)[['transaction_id', 'transaction_amount_usd', 'is_laundering', 'anomaly_score', 'is_anomaly_predicted']].head(5))