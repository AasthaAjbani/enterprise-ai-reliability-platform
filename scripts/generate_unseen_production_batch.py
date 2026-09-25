from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

PRODUCTION_DIR = (
    PROJECT_ROOT
    / "data"
    / "production"
)

SOURCE_DATA_FILE = (
    PRODUCTION_DIR
    / "transactions_production.csv"
)

OUTPUT_DATA_FILE = (
    PRODUCTION_DIR
    / "transactions_production_batch_2.csv"
)

METADATA_FILE = (
    PRODUCTION_DIR
    / "transactions_production_batch_2_metadata.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 20260924

BATCH_SIZE = 5000

TARGET_FRAUD_RATE = 0.08


# ============================================================
# RANDOM GENERATOR
# ============================================================

rng = np.random.default_rng(
    RANDOM_SEED
)


# ============================================================
# SIGMOID
# ============================================================

def sigmoid(
    values: np.ndarray,
) -> np.ndarray:

    return (
        1.0
        /
        (
            1.0
            +
            np.exp(
                -values
            )
        )
    )


# ============================================================
# FIND INTERCEPT FOR TARGET FRAUD RATE
# ============================================================

def find_intercept(
    base_score: np.ndarray,
    target_rate: float,
) -> float:

    """
    Find an intercept so that the average fraud
    probability is close to TARGET_FRAUD_RATE.
    """

    lower = -15.0

    upper = 15.0


    for _ in range(
        100
    ):

        midpoint = (
            lower
            +
            upper
        ) / 2.0


        probabilities = (
            sigmoid(
                base_score
                +
                midpoint
            )
        )


        average_probability = (
            probabilities.mean()
        )


        if (
            average_probability
            >
            target_rate
        ):

            upper = midpoint

        else:

            lower = midpoint


    return (
        lower
        +
        upper
    ) / 2.0


# ============================================================
# GENERATE BATCH
# ============================================================

def generate_batch() -> pd.DataFrame:

    # --------------------------------------------------------
    # Validate source file
    # --------------------------------------------------------

    if not SOURCE_DATA_FILE.exists():

        raise FileNotFoundError(
            "Existing production dataset not found:\n"
            f"{SOURCE_DATA_FILE}"
        )


    # --------------------------------------------------------
    # Load current production data
    # --------------------------------------------------------

    source = pd.read_csv(
        SOURCE_DATA_FILE
    )


    print(
        f"Loaded source production rows: "
        f"{len(source)}"
    )


    # --------------------------------------------------------
    # Sample existing rows
    #
    # This preserves real category names and schema.
    # --------------------------------------------------------

    sampled_indices = (
        rng.choice(
            source.index.to_numpy(),
            size=BATCH_SIZE,
            replace=True,
        )
    )


    batch = (
        source
        .loc[
            sampled_indices
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )


    # --------------------------------------------------------
    # NEW TRANSACTION IDS
    # --------------------------------------------------------

    batch[
        "transaction_id"
    ] = [

        f"BATCH2_{index:07d}"

        for index in range(
            1,
            BATCH_SIZE + 1,
        )
    ]


    # ========================================================
    # FEATURE DISTRIBUTION SHIFT
    # ========================================================

    # --------------------------------------------------------
    # Transaction amount
    #
    # New fraud wave contains more low / medium value
    # transactions instead of obvious high-value fraud.
    # --------------------------------------------------------

    amount_noise = (
        rng.normal(
            loc=1.0,
            scale=0.15,
            size=BATCH_SIZE,
        )
    )


    batch[
        "transaction_amount"
    ] = (

        batch[
            "transaction_amount"
        ]
        *
        0.60
        *
        amount_noise

    ).clip(
        lower=1.0
    )


    # --------------------------------------------------------
    # Account age
    #
    # Fraud increasingly occurs on older trusted accounts.
    # --------------------------------------------------------

    batch[
        "account_age_days"
    ] = (

        batch[
            "account_age_days"
        ]
        *
        rng.uniform(
            1.2,
            1.8,
            BATCH_SIZE,
        )

    ).round()


    batch[
        "account_age_days"
    ] = (

        batch[
            "account_age_days"
        ]
        .clip(
            lower=1
        )
        .astype(int)
    )


    # --------------------------------------------------------
    # Previous transactions
    #
    # More activity comes from established accounts.
    # --------------------------------------------------------

    additional_transactions = (
        rng.poisson(
            lam=10,
            size=BATCH_SIZE,
        )
    )


    batch[
        "previous_transactions"
    ] = (

        batch[
            "previous_transactions"
        ]
        +
        additional_transactions
    )


    # --------------------------------------------------------
    # Failed transactions
    #
    # Account takeover fraud avoids repeated failed attempts.
    # --------------------------------------------------------

    original_failed = (
        batch[
            "failed_transactions_last_24h"
        ]
        .to_numpy()
    )


    reduced_failed = (
        original_failed
        *
        rng.uniform(
            0.0,
            0.35,
            BATCH_SIZE,
        )
    )


    batch[
        "failed_transactions_last_24h"
    ] = (

        np.floor(
            reduced_failed
        )
        .astype(int)
    )


    # --------------------------------------------------------
    # International behavior
    #
    # Most of the new fraud pattern is domestic.
    # --------------------------------------------------------

    batch[
        "is_international"
    ] = (
        rng.choice(
            [0, 1],
            size=BATCH_SIZE,
            p=[
                0.94,
                0.06,
            ],
        )
    )


    # --------------------------------------------------------
    # Transaction hours
    #
    # Increase unusual late-night activity.
    # --------------------------------------------------------

    night_mask = (
        rng.random(
            BATCH_SIZE
        )
        <
        0.55
    )


    night_hours = (
        rng.choice(
            [
                0,
                1,
                2,
                3,
                4,
                5,
                22,
                23,
            ],
            size=BATCH_SIZE,
        )
    )


    regular_hours = (
        rng.integers(
            6,
            22,
            size=BATCH_SIZE,
        )
    )


    batch[
        "transaction_hour"
    ] = (
        np.where(
            night_mask,
            night_hours,
            regular_hours,
        )
    )


    # ========================================================
    # NEW FRAUD CONCEPT
    # ========================================================

    # The new fraud mechanism deliberately represents
    # concept drift:
    #
    # fraud is increasingly associated with:
    #
    # - low / medium transaction amounts
    # - established accounts
    # - domestic transactions
    # - very few failed attempts
    # - night activity
    # - accounts with long transaction histories


    amount_q40 = (
        batch[
            "transaction_amount"
        ]
        .quantile(
            0.40
        )
    )


    account_q65 = (
        batch[
            "account_age_days"
        ]
        .quantile(
            0.65
        )
    )


    previous_q65 = (
        batch[
            "previous_transactions"
        ]
        .quantile(
            0.65
        )
    )


    low_amount = (

        batch[
            "transaction_amount"
        ]
        <=
        amount_q40

    ).astype(float)


    established_account = (

        batch[
            "account_age_days"
        ]
        >=
        account_q65

    ).astype(float)


    high_history = (

        batch[
            "previous_transactions"
        ]
        >=
        previous_q65

    ).astype(float)


    low_failed_attempts = (

        batch[
            "failed_transactions_last_24h"
        ]
        <=
        1

    ).astype(float)


    domestic = (

        batch[
            "is_international"
        ]
        ==
        0

    ).astype(float)


    unusual_hour = (

        (
            batch[
                "transaction_hour"
            ]
            <=
            5
        )

        |

        (
            batch[
                "transaction_hour"
            ]
            >=
            22
        )

    ).astype(float)


    # --------------------------------------------------------
    # Fraud risk score for NEW concept
    # --------------------------------------------------------

    base_score = (

        1.60
        *
        low_amount

        +

        1.35
        *
        unusual_hour

        +

        1.15
        *
        established_account

        +

        1.00
        *
        high_history

        +

        0.90
        *
        low_failed_attempts

        +

        0.60
        *
        domestic

        +

        rng.normal(
            loc=0.0,
            scale=0.55,
            size=BATCH_SIZE,
        )
    ).to_numpy()


    # --------------------------------------------------------
    # Calibrate fraud probability
    # --------------------------------------------------------

    intercept = (
        find_intercept(
            base_score,
            TARGET_FRAUD_RATE,
        )
    )


    fraud_probability = (
        sigmoid(
            base_score
            +
            intercept
        )
    )


    # --------------------------------------------------------
    # Generate labels
    # --------------------------------------------------------

    batch[
        "is_fraud"
    ] = (

        rng.random(
            BATCH_SIZE
        )
        <
        fraud_probability

    ).astype(int)


    return batch


# ============================================================
# SAVE BATCH
# ============================================================

def save_batch(
    batch: pd.DataFrame,
) -> None:

    PRODUCTION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    batch.to_csv(
        OUTPUT_DATA_FILE,
        index=False,
    )


    fraud_count = int(
        batch[
            "is_fraud"
        ].sum()
    )


    fraud_rate = float(
        batch[
            "is_fraud"
        ].mean()
    )


    metadata = {

        "batch_name":
            "production_batch_2",

        "random_seed":
            RANDOM_SEED,

        "rows":
            int(
                len(batch)
            ),

        "fraud_count":
            fraud_count,

        "fraud_rate":
            fraud_rate,

        "target_fraud_rate":
            TARGET_FRAUD_RATE,

        "scenario":
            (
                "Concept drift caused by fraud moving "
                "toward low-value domestic transactions "
                "on established accounts with fewer "
                "failed attempts."
            ),

        "output_file":
            str(
                OUTPUT_DATA_FILE
            ),
    }


    with METADATA_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
        )


    print()
    print("=" * 70)
    print("UNSEEN PRODUCTION BATCH GENERATED")
    print("=" * 70)

    print(
        f"\nRows: "
        f"{len(batch)}"
    )

    print(
        f"Fraud rows: "
        f"{fraud_count}"
    )

    print(
        f"Fraud rate: "
        f"{fraud_rate:.4%}"
    )

    print(
        f"\nDataset:"
        f"\n{OUTPUT_DATA_FILE}"
    )

    print(
        f"\nMetadata:"
        f"\n{METADATA_FILE}"
    )

    print()


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("GENERATING UNSEEN PRODUCTION BATCH 2")
    print("=" * 70)
    print()

    batch = (
        generate_batch()
    )

    save_batch(
        batch
    )


if __name__ == "__main__":
    main()