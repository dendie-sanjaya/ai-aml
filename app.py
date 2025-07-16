# app.py

from flask import Flask, request, jsonify
import json
import joblib
import pandas as pd
import numpy as np
import os # Untuk mengecek keberadaan file

app = Flask(__name__)

# --- Konfigurasi Model dan Preprocessor ---
MODEL_PATH = 'aml_isolation_forest_model.pkl'
PREPROCESSOR_PATH = 'aml_preprocessor.pkl'

# Define the features that the model expects (must match training features order)
# Pastikan ini sesuai dengan fitur yang digunakan saat training, termasuk nama kolom USD
numerical_features = [
    'transaction_amount_usd', # Ubah dari IDR ke USD
    'transaction_frequency_30d',
    'avg_daily_balance_30d',
    'transaction_hour',
    'num_flagged_transactions_sender_90d'
]
categorical_features = [
    'sender_account_type',
    'receiver_account_type',
    'is_international',
    'ip_country_match'
]
expected_features = numerical_features + categorical_features

# Load the trained model and preprocessor globally when the app starts
# This avoids loading them on every request, which would be inefficient
model = None
preprocessor = None

if os.path.exists(MODEL_PATH) and os.path.exists(PREPROCESSOR_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("Model and preprocessor loaded successfully.")
    except Exception as e:
        print(f"Error loading model or preprocessor: {e}")
        print("Please ensure 'aml_isolation_forest_model.pkl' and 'aml_preprocessor.pkl' exist and are valid.")
        # Exit or handle gracefully if model cannot be loaded
else:
    print(f"Error: Model file '{MODEL_PATH}' or preprocessor file '{PREPROCESSOR_PATH}' not found.")
    print("Please ensure you have run the data generation and model training scripts first.")
    # In a production environment, you might want to raise an error or prevent the app from starting.


@app.route('/predict_aml', methods=['POST'])
def predict_aml_api():
    """
    RESTful API endpoint to predict money laundering risk for a transaction.
    Expects a JSON payload with transaction parameters.
    """
    if model is None or preprocessor is None:
        return jsonify({"error": "AI model not loaded. Please check server logs."}), 500

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    transaction_params = request.get_json()

    # Basic validation for required features
    for feature in expected_features:
        if feature not in transaction_params:
            return jsonify({"error": f"Missing required parameter: '{feature}'"}), 400

    try:
        # Convert to DataFrame
        # Ensure the order of columns matches the training data features
        input_df = pd.DataFrame([transaction_params], columns=expected_features)

        # Preprocess the input data
        processed_input = preprocessor.transform(input_df)

        # Get the anomaly score from the Isolation Forest model
        anomaly_score = model.decision_function(processed_input)[0]

        # Convert anomaly score to a "probability" or "risk score"
        # Clamp score to a reasonable range for scaling
        clamped_score = np.clip(anomaly_score, -0.5, 0.5) # Adjust range based on your model's typical scores
        risk_probability = (0.5 - clamped_score) / 1.0 # Simple linear scaling
        risk_probability = np.clip(risk_probability, 0.0, 1.0) # Ensure between 0 and 1

        # Determine if it's considered money laundering based on a threshold
        is_money_laundering = 1 if anomaly_score < model.offset_ else 0

        # --- Generate Explanation ---
        # Initialize explanation based on the prediction
        if is_money_laundering:
            explanation = "This transaction shows unusual patterns. It is flagged as potentially suspicious, suggesting a higher risk of money laundering."
            # Add specific details that trigger the anomaly (adjust based on your features)
            if 'transaction_amount_usd' in transaction_params and transaction_params['transaction_amount_usd'] > 10000: # Example USD threshold
                explanation += " (Very high amount detected)."
            if 'transaction_frequency_30d' in transaction_params and transaction_params['transaction_frequency_30d'] < 5:
                explanation += " (Unusually low frequency)."
            if 'is_international' in transaction_params and transaction_params['is_international'] == 1 and \
               'ip_country_match' in transaction_params and transaction_params['ip_country_match'] == 0:
                explanation += " (International transaction with mismatched IP)."
            if 'num_flagged_transactions_sender_90d' in transaction_params and transaction_params['num_flagged_transactions_sender_90d'] > 0:
                explanation += " (Sender has past flagged transactions)."
        else:
            explanation = "This transaction looks normal, indicating a lower risk."

        response_data = {
            "transaction_id": transaction_params.get('transaction_id', 'N/A'),
            "is_money_laundering": bool(is_money_laundering),
            "aml_risk_probability": round(float(risk_probability), 4),
            "anomaly_score": round(float(anomaly_score), 4), # For debugging/understanding
            "explanation": explanation
        }

        return jsonify(response_data), 200

    except KeyError as ke:
        return jsonify({"error": f"Missing expected feature in input: {ke}. Please check your JSON payload."}), 400
    except ValueError as ve:
        return jsonify({"error": f"Invalid data type or value in input: {ve}. Ensure numerical values are numbers."}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Untuk menjalankan aplikasi Flask
if __name__ == '__main__':
    # Pastikan Anda sudah menjalankan script data generation dan model training
    # sebelum menjalankan app.py ini.
    # Contoh:
    # 1. python generate_aml_data.py
    # 2. python train_aml_model.py
    # 3. python app.py
    app.run(debug=True, host='0.0.0.0', port=5000)
