from pathlib import Path

import joblib
import pandas as pd


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_FILE = PROJECT_ROOT / "models" / "fraud_model.joblib"


# ---------------------------------------------------------
# 2. LOAD TRAINED MODEL
# ---------------------------------------------------------

print("\nLoading trained fraud model...")

model = joblib.load(MODEL_FILE)

print("Model loaded successfully.")


# ---------------------------------------------------------
# 3. SAMPLE TRANSACTION
# ---------------------------------------------------------

transaction = {
    "customer_age": 24,
    "transaction_amount": 22000,
    "transaction_hour": 2,
    "payment_method": "Credit Card",
    "device_type": "Mobile",
    "customer_location": "Delhi",
    "account_age_days": 8,
    "previous_transactions": 2,
    "failed_transactions_last_24h": 4,
    "is_international": 1,
}


# Convert dictionary into dataframe
transaction_df = pd.DataFrame(
    [transaction]
)


# ---------------------------------------------------------
# 4. MAKE PREDICTION
# ---------------------------------------------------------

prediction = model.predict(
    transaction_df
)[0]

probabilities = model.predict_proba(
    transaction_df
)[0]


fraud_probability = probabilities[1]


# ---------------------------------------------------------
# 5. DISPLAY RESULT
# ---------------------------------------------------------

print("\n-----------------------------------")
print("TRANSACTION ANALYSIS")
print("-----------------------------------")

for key, value in transaction.items():
    print(f"{key}: {value}")


print("\n-----------------------------------")

print(
    f"Fraud Prediction: "
    f"{'FRAUD' if prediction == 1 else 'LEGITIMATE'}"
)

print(
    f"Fraud Probability: "
    f"{fraud_probability * 100:.2f}%"
)

print("-----------------------------------")