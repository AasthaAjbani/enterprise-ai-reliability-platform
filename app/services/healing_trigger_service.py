from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

ACTIVE_MODEL_PATH = (
    MODELS_DIR
    / "fraud_model.joblib"
)

BASELINE_METRICS_PATH = (
    MODELS_DIR
    / "baseline_metrics.json"
)

PRODUCTION_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)


# =========================================================
# MODEL FEATURES
# =========================================================

TARGET_COLUMN = "is_fraud"


FEATURE_COLUMNS = [
    "payment_method",
    "device_type",
    "customer_location",
    "customer_age",
    "transaction_amount",
    "transaction_hour",
    "account_age_days",
    "previous_transactions",
    "failed_transactions_last_24h",
    "is_international",
]


# =========================================================
# THRESHOLDS
# =========================================================

WARNING_DROP = 0.05

CRITICAL_DROP = 0.15


# =========================================================
# LOAD BASELINE
# =========================================================

def load_baseline_metrics():

    if not BASELINE_METRICS_PATH.exists():

        raise FileNotFoundError(
            "Baseline metrics not found:\n"
            f"{BASELINE_METRICS_PATH}"
        )


    with open(
        BASELINE_METRICS_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# CALCULATE ACTIVE PERFORMANCE
# =========================================================

def calculate_active_performance():

    if not ACTIVE_MODEL_PATH.exists():

        raise FileNotFoundError(
            "Active production model not found:\n"
            f"{ACTIVE_MODEL_PATH}"
        )


    if not PRODUCTION_DATA_PATH.exists():

        raise FileNotFoundError(
            "Production dataset not found:\n"
            f"{PRODUCTION_DATA_PATH}"
        )


    model = joblib.load(
        ACTIVE_MODEL_PATH
    )


    production_data = pd.read_csv(
        PRODUCTION_DATA_PATH
    )


    X = production_data[
        FEATURE_COLUMNS
    ]

    y = production_data[
        TARGET_COLUMN
    ]


    predictions = model.predict(
        X
    )


    return {

        "accuracy":
            float(
                accuracy_score(
                    y,
                    predictions,
                )
            ),

        "precision":
            float(
                precision_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),

        "recall":
            float(
                recall_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),

        "f1":
            float(
                f1_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),
    }


# =========================================================
# HEALING TRIGGER
# =========================================================

def evaluate_healing_trigger():

    baseline = (
        load_baseline_metrics()
    )


    production = (
        calculate_active_performance()
    )


    f1_drop = (
        baseline["f1"]
        -
        production["f1"]
    )


    recall_drop = (
        baseline["recall"]
        -
        production["recall"]
    )


    # -----------------------------------------------------
    # Reliability status
    # -----------------------------------------------------

    if (
        f1_drop >= CRITICAL_DROP
        or
        recall_drop >= CRITICAL_DROP
    ):

        status = "CRITICAL"

    elif (
        f1_drop >= WARNING_DROP
        or
        recall_drop >= WARNING_DROP
    ):

        status = "WARNING"

    else:

        status = "HEALTHY"


    # -----------------------------------------------------
    # We only automatically heal CRITICAL degradation.
    #
    # WARNING means continue monitoring.
    # -----------------------------------------------------

    healing_required = (
        status == "CRITICAL"
    )


    if healing_required:

        reason = (
            "Critical model performance degradation "
            "detected."
        )

    elif status == "WARNING":

        reason = (
            "Moderate degradation detected. "
            "Continue monitoring before retraining."
        )

    else:

        reason = (
            "Active model performance is within "
            "acceptable reliability thresholds."
        )


    return {

        "status":
            status,

        "healing_required":
            healing_required,

        "reason":
            reason,

        "thresholds": {

            "warning_drop":
                WARNING_DROP,

            "critical_drop":
                CRITICAL_DROP,
        },

        "baseline": {

            "accuracy":
                baseline["accuracy"],

            "precision":
                baseline["precision"],

            "recall":
                baseline["recall"],

            "f1":
                baseline["f1"],
        },

        "production": production,

        "degradation": {

            "f1_drop":
                float(
                    f1_drop
                ),

            "recall_drop":
                float(
                    recall_drop
                ),
        },
    }