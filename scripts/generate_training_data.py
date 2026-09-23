import os
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REFERENCE_DATA_DIR = PROJECT_ROOT / "data" / "reference"

OUTPUT_FILE = REFERENCE_DATA_DIR / "transactions_reference.csv"


# ---------------------------------------------------------
# 2. CONFIGURATION
# ---------------------------------------------------------

RANDOM_SEED = 42
NUMBER_OF_TRANSACTIONS = 10_000

np.random.seed(RANDOM_SEED)


# ---------------------------------------------------------
# 3. GENERATE BASIC TRANSACTION DATA
# ---------------------------------------------------------

transaction_ids = np.arange(1, NUMBER_OF_TRANSACTIONS + 1)

customer_age = np.random.normal(
    loc=35,
    scale=10,
    size=NUMBER_OF_TRANSACTIONS
)

customer_age = np.clip(
    customer_age,
    18,
    80
).astype(int)


transaction_amount = np.random.lognormal(
    mean=7.4,
    sigma=0.8,
    size=NUMBER_OF_TRANSACTIONS
)

transaction_amount = np.round(
    np.clip(transaction_amount, 100, 50_000),
    2
)


transaction_hour = np.random.randint(
    0,
    24,
    NUMBER_OF_TRANSACTIONS
)


payment_method = np.random.choice(
    ["UPI", "Credit Card", "Debit Card", "Net Banking"],
    size=NUMBER_OF_TRANSACTIONS,
    p=[0.40, 0.30, 0.20, 0.10]
)


device_type = np.random.choice(
    ["Mobile", "Desktop", "Tablet"],
    size=NUMBER_OF_TRANSACTIONS,
    p=[0.65, 0.28, 0.07]
)


customer_location = np.random.choice(
    ["Jaipur", "Delhi", "Mumbai", "Bengaluru", "Pune", "Ahmedabad"],
    size=NUMBER_OF_TRANSACTIONS,
    p=[0.15, 0.20, 0.20, 0.20, 0.15, 0.10]
)


account_age_days = np.random.exponential(
    scale=500,
    size=NUMBER_OF_TRANSACTIONS
)

account_age_days = np.clip(
    account_age_days,
    1,
    3000
).astype(int)


previous_transactions = np.random.poisson(
    lam=25,
    size=NUMBER_OF_TRANSACTIONS
)


failed_transactions_last_24h = np.random.poisson(
    lam=0.4,
    size=NUMBER_OF_TRANSACTIONS
)


is_international = np.random.choice(
    [0, 1],
    size=NUMBER_OF_TRANSACTIONS,
    p=[0.94, 0.06]
)


# ---------------------------------------------------------
# 4. CREATE FRAUD PROBABILITY
# ---------------------------------------------------------

fraud_probability = np.full(
    NUMBER_OF_TRANSACTIONS,
    0.01
)


# High transaction values are slightly more suspicious
fraud_probability += np.where(
    transaction_amount > 15_000,
    0.12,
    0
)


# Transactions during unusual hours
fraud_probability += np.where(
    (transaction_hour >= 0) & (transaction_hour <= 4),
    0.08,
    0
)


# Very new accounts
fraud_probability += np.where(
    account_age_days < 30,
    0.12,
    0
)


# Multiple recent failed transactions
fraud_probability += np.where(
    failed_transactions_last_24h >= 3,
    0.18,
    0
)


# International transactions
fraud_probability += np.where(
    is_international == 1,
    0.10,
    0
)


# Large credit card transactions receive slightly higher risk
fraud_probability += np.where(
    (payment_method == "Credit Card")
    & (transaction_amount > 10_000),
    0.07,
    0
)


# Extremely high-risk combination
fraud_probability += np.where(
    (account_age_days < 15)
    & (transaction_amount > 20_000),
    0.25,
    0
)


# Probability must always remain between 0 and 1
fraud_probability = np.clip(
    fraud_probability,
    0,
    0.95
)


# ---------------------------------------------------------
# 5. GENERATE FRAUD LABEL
# ---------------------------------------------------------

is_fraud = np.random.binomial(
    n=1,
    p=fraud_probability
)


# ---------------------------------------------------------
# 6. CREATE DATAFRAME
# ---------------------------------------------------------

transactions = pd.DataFrame(
    {
        "transaction_id": transaction_ids,
        "customer_age": customer_age,
        "transaction_amount": transaction_amount,
        "transaction_hour": transaction_hour,
        "payment_method": payment_method,
        "device_type": device_type,
        "customer_location": customer_location,
        "account_age_days": account_age_days,
        "previous_transactions": previous_transactions,
        "failed_transactions_last_24h": failed_transactions_last_24h,
        "is_international": is_international,
        "is_fraud": is_fraud,
    }
)


# ---------------------------------------------------------
# 7. SAVE DATASET
# ---------------------------------------------------------

REFERENCE_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

transactions.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# 8. PRINT DATASET SUMMARY
# ---------------------------------------------------------

print("\nReference dataset generated successfully.")
print(f"File saved at: {OUTPUT_FILE}")

print("\nDataset shape:")
print(transactions.shape)

print("\nFirst 5 rows:")
print(transactions.head())

print("\nFraud distribution:")
print(transactions["is_fraud"].value_counts())

print("\nFraud percentage:")
fraud_percentage = transactions["is_fraud"].mean() * 100
print(f"{fraud_percentage:.2f}%")

print("\nAverage transaction amount:")
print(f"₹{transactions['transaction_amount'].mean():.2f}")

print("\nPayment method distribution:")
print(
    transactions["payment_method"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nDevice distribution:")
print(
    transactions["device_type"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)