from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCTION_DATA_DIR = PROJECT_ROOT / "data" / "production"

OUTPUT_FILE = PRODUCTION_DATA_DIR / "transactions_production.csv"


# ---------------------------------------------------------
# 2. CONFIGURATION
# ---------------------------------------------------------

RANDOM_SEED = 99
NUMBER_OF_TRANSACTIONS = 5000

np.random.seed(RANDOM_SEED)


# ---------------------------------------------------------
# 3. GENERATE PRODUCTION TRANSACTION DATA
# ---------------------------------------------------------

transaction_ids = np.arange(
    10001,
    10001 + NUMBER_OF_TRANSACTIONS
)


customer_age = np.random.normal(
    loc=34,
    scale=11,
    size=NUMBER_OF_TRANSACTIONS
)

customer_age = np.clip(
    customer_age,
    18,
    80
).astype(int)


# ---------------------------------------------------------
# INTENTIONAL DRIFT 1:
# Transaction values are now higher
# ---------------------------------------------------------

transaction_amount = np.random.lognormal(
    mean=8.0,
    sigma=0.9,
    size=NUMBER_OF_TRANSACTIONS
)

transaction_amount = np.round(
    np.clip(
        transaction_amount,
        100,
        70000
    ),
    2
)


# ---------------------------------------------------------
# INTENTIONAL DRIFT 2:
# More transactions happen late at night
# ---------------------------------------------------------

normal_hours = np.random.randint(
    6,
    24,
    size=int(NUMBER_OF_TRANSACTIONS * 0.75)
)

night_hours = np.random.randint(
    0,
    6,
    size=int(NUMBER_OF_TRANSACTIONS * 0.25)
)

transaction_hour = np.concatenate(
    [
        normal_hours,
        night_hours
    ]
)

np.random.shuffle(
    transaction_hour
)


# ---------------------------------------------------------
# INTENTIONAL DRIFT 3:
# UPI usage increased strongly
# ---------------------------------------------------------

payment_method = np.random.choice(
    [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Net Banking"
    ],
    size=NUMBER_OF_TRANSACTIONS,
    p=[
        0.68,
        0.17,
        0.10,
        0.05
    ]
)


# ---------------------------------------------------------
# INTENTIONAL DRIFT 4:
# Mobile usage increased
# ---------------------------------------------------------

device_type = np.random.choice(
    [
        "Mobile",
        "Desktop",
        "Tablet"
    ],
    size=NUMBER_OF_TRANSACTIONS,
    p=[
        0.82,
        0.14,
        0.04
    ]
)


customer_location = np.random.choice(
    [
        "Jaipur",
        "Delhi",
        "Mumbai",
        "Bengaluru",
        "Pune",
        "Ahmedabad"
    ],
    size=NUMBER_OF_TRANSACTIONS,
    p=[
        0.12,
        0.23,
        0.21,
        0.19,
        0.15,
        0.10
    ]
)


# ---------------------------------------------------------
# INTENTIONAL DRIFT 5:
# More new accounts
# ---------------------------------------------------------

account_age_days = np.random.exponential(
    scale=300,
    size=NUMBER_OF_TRANSACTIONS
)

account_age_days = np.clip(
    account_age_days,
    1,
    3000
).astype(int)


previous_transactions = np.random.poisson(
    lam=20,
    size=NUMBER_OF_TRANSACTIONS
)


# ---------------------------------------------------------
# INTENTIONAL DRIFT 6:
# Failed transactions increased
# ---------------------------------------------------------

failed_transactions_last_24h = np.random.poisson(
    lam=0.9,
    size=NUMBER_OF_TRANSACTIONS
)


# ---------------------------------------------------------
# INTENTIONAL DRIFT 7:
# More international transactions
# ---------------------------------------------------------

is_international = np.random.choice(
    [0, 1],
    size=NUMBER_OF_TRANSACTIONS,
    p=[
        0.88,
        0.12
    ]
)


# ---------------------------------------------------------
# 4. CREATE FRAUD PROBABILITY
# ---------------------------------------------------------

fraud_probability = np.full(
    NUMBER_OF_TRANSACTIONS,
    0.015
)


fraud_probability += np.where(
    transaction_amount > 15000,
    0.12,
    0
)


fraud_probability += np.where(
    transaction_hour <= 4,
    0.08,
    0
)


fraud_probability += np.where(
    account_age_days < 30,
    0.12,
    0
)


fraud_probability += np.where(
    failed_transactions_last_24h >= 3,
    0.18,
    0
)


fraud_probability += np.where(
    is_international == 1,
    0.10,
    0
)


fraud_probability += np.where(
    (
        payment_method == "Credit Card"
    )
    &
    (
        transaction_amount > 10000
    ),
    0.07,
    0
)


fraud_probability += np.where(
    (
        account_age_days < 15
    )
    &
    (
        transaction_amount > 20000
    ),
    0.25,
    0
)


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
# 7. SAVE PRODUCTION DATA
# ---------------------------------------------------------

PRODUCTION_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

transactions.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# 8. PRINT SUMMARY
# ---------------------------------------------------------

print(
    "\nProduction dataset generated successfully."
)

print(
    f"File saved at: {OUTPUT_FILE}"
)

print(
    f"\nDataset shape: {transactions.shape}"
)

print(
    "\nFraud percentage:"
)

print(
    f"{transactions['is_fraud'].mean() * 100:.2f}%"
)

print(
    "\nAverage transaction amount:"
)

print(
    f"₹{transactions['transaction_amount'].mean():.2f}"
)

print(
    "\nPayment method distribution:"
)

print(
    transactions[
        "payment_method"
    ]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)

print(
    "\nDevice type distribution:"
)

print(
    transactions[
        "device_type"
    ]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)

print(
    "\nInternational transaction distribution:"
)

print(
    transactions[
        "is_international"
    ]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)