from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production_corrupted.csv"
)


# ---------------------------------------------------------
# 2. LOAD CLEAN PRODUCTION DATA
# ---------------------------------------------------------

print("\nLoading clean production data...")

data = pd.read_csv(
    INPUT_FILE
)

print(
    f"Loaded {len(data)} rows."
)


# ---------------------------------------------------------
# 3. CREATE COPY
# ---------------------------------------------------------

corrupted_data = data.copy()


# ---------------------------------------------------------
# 4. INJECT MISSING VALUES
# ---------------------------------------------------------

missing_indices = corrupted_data.sample(
    n=20,
    random_state=1
).index

corrupted_data.loc[
    missing_indices[:10],
    "device_type"
] = np.nan

corrupted_data.loc[
    missing_indices[10:],
    "customer_age"
] = np.nan


# ---------------------------------------------------------
# 5. INVALID CUSTOMER AGE
# ---------------------------------------------------------

age_indices = corrupted_data.sample(
    n=10,
    random_state=2
).index

corrupted_data.loc[
    age_indices[:5],
    "customer_age"
] = -5

corrupted_data.loc[
    age_indices[5:],
    "customer_age"
] = 150


# ---------------------------------------------------------
# 6. INVALID TRANSACTION AMOUNT
# ---------------------------------------------------------

amount_indices = corrupted_data.sample(
    n=8,
    random_state=3
).index

corrupted_data.loc[
    amount_indices,
    "transaction_amount"
] = -1000


# ---------------------------------------------------------
# 7. INVALID TRANSACTION HOUR
# ---------------------------------------------------------

hour_indices = corrupted_data.sample(
    n=6,
    random_state=4
).index

corrupted_data.loc[
    hour_indices[:3],
    "transaction_hour"
] = -2

corrupted_data.loc[
    hour_indices[3:],
    "transaction_hour"
] = 30


# ---------------------------------------------------------
# 8. UNKNOWN PAYMENT METHOD
# ---------------------------------------------------------

payment_indices = corrupted_data.sample(
    n=12,
    random_state=5
).index

corrupted_data.loc[
    payment_indices,
    "payment_method"
] = "CryptoPay"


# ---------------------------------------------------------
# 9. UNKNOWN DEVICE TYPE
# ---------------------------------------------------------

device_indices = corrupted_data.sample(
    n=8,
    random_state=6
).index

corrupted_data.loc[
    device_indices,
    "device_type"
] = "SmartWatch"


# ---------------------------------------------------------
# 10. INVALID INTERNATIONAL FLAG
# ---------------------------------------------------------

international_indices = corrupted_data.sample(
    n=5,
    random_state=7
).index

corrupted_data.loc[
    international_indices,
    "is_international"
] = 3


# ---------------------------------------------------------
# 11. CREATE DUPLICATE TRANSACTION IDS
# ---------------------------------------------------------

duplicate_indices = corrupted_data.sample(
    n=10,
    random_state=8
).index

duplicate_transaction_id = (
    corrupted_data.loc[
        corrupted_data.index[0],
        "transaction_id"
    ]
)

corrupted_data.loc[
    duplicate_indices,
    "transaction_id"
] = duplicate_transaction_id


# ---------------------------------------------------------
# 12. SAVE CORRUPTED DATA
# ---------------------------------------------------------

corrupted_data.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "\nCorrupted production dataset created successfully."
)

print(
    f"Saved at: {OUTPUT_FILE}"
)

print(
    "\nInjected issues:"
)

print(
    " - Missing values"
)

print(
    " - Invalid customer ages"
)

print(
    " - Negative transaction amounts"
)

print(
    " - Invalid transaction hours"
)

print(
    " - Unknown payment methods"
)

print(
    " - Unknown device types"
)

print(
    " - Invalid international flags"
)

print(
    " - Duplicate transaction IDs"
)