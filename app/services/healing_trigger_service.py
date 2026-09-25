from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

from app.services.active_model_baseline_service import (
    get_active_model_baseline,
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

ACTIVE_MODEL_PATH = (
    MODELS_DIR
    / "fraud_model.joblib"
)

DEFAULT_PRODUCTION_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)


# =========================================================
# RESOLVE PRODUCTION DATASET
# =========================================================

def resolve_production_data_path(
    production_data_path: Path | None = None,
) -> Path:

    """
    Decide which production dataset should be used.

    Priority:

    1. Explicit path passed to function
    2. HEALING_PRODUCTION_DATA environment variable
    3. Default transactions_production.csv
    """

    # -----------------------------------------------------
    # Explicit path supplied
    # -----------------------------------------------------

    if production_data_path is not None:

        path = Path(
            production_data_path
        )

        if not path.is_absolute():

            path = (
                PROJECT_ROOT
                / path
            )

        return path.resolve()


    # -----------------------------------------------------
    # Environment variable
    # -----------------------------------------------------

    environment_path = os.getenv(
        "HEALING_PRODUCTION_DATA"
    )


    if environment_path:

        path = Path(
            environment_path
        )

        if not path.is_absolute():

            path = (
                PROJECT_ROOT
                / path
            )

        return path.resolve()


    # -----------------------------------------------------
    # Default production dataset
    # -----------------------------------------------------

    return (
        DEFAULT_PRODUCTION_DATA_PATH
        .resolve()
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
# CALCULATE ACTIVE PERFORMANCE
# =========================================================

def calculate_active_performance(
    production_data_path: Path | None = None,
) -> dict[str, float]:

    """
    Evaluate the currently deployed champion model
    on the selected production dataset.
    """

    # -----------------------------------------------------
    # Resolve dataset path
    # -----------------------------------------------------

    production_data_path = (
        resolve_production_data_path(
            production_data_path
        )
    )


    # -----------------------------------------------------
    # Validate active model
    # -----------------------------------------------------

    if not ACTIVE_MODEL_PATH.exists():

        raise FileNotFoundError(
            "Active production model not found:\n"
            f"{ACTIVE_MODEL_PATH}"
        )


    # -----------------------------------------------------
    # Validate production dataset
    # -----------------------------------------------------

    if not production_data_path.exists():

        raise FileNotFoundError(
            "Production dataset not found:\n"
            f"{production_data_path}"
        )


    # -----------------------------------------------------
    # Load model
    # -----------------------------------------------------

    model = joblib.load(
        ACTIVE_MODEL_PATH
    )


    # -----------------------------------------------------
    # Load production data
    # -----------------------------------------------------

    production_data = pd.read_csv(
        production_data_path
    )


    # -----------------------------------------------------
    # Required columns
    # -----------------------------------------------------

    required_columns = (
        FEATURE_COLUMNS
        +
        [TARGET_COLUMN]
    )


    missing_columns = [
        column
        for column in required_columns
        if column
        not in production_data.columns
    ]


    if missing_columns:

        raise ValueError(
            "Production dataset is missing "
            "required columns: "
            f"{missing_columns}"
        )


    # -----------------------------------------------------
    # Features and labels
    # -----------------------------------------------------

    X = production_data[
        FEATURE_COLUMNS
    ]


    y = production_data[
        TARGET_COLUMN
    ]


    # -----------------------------------------------------
    # Predictions
    # -----------------------------------------------------

    predictions = model.predict(
        X
    )


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

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

def evaluate_healing_trigger(
    production_data_path: Path | None = None,
) -> dict[str, Any]:

    """
    Determine whether autonomous healing should start.

    The deployed model is compared against the baseline
    belonging to the currently active champion model.
    """


    # -----------------------------------------------------
    # Resolve production dataset
    # -----------------------------------------------------

    evaluated_dataset = (
        resolve_production_data_path(
            production_data_path
        )
    )


    # -----------------------------------------------------
    # Load active champion baseline
    # -----------------------------------------------------

    active_baseline = (
        get_active_model_baseline()
    )


    baseline = (
        active_baseline[
            "metrics"
        ]
    )


    # -----------------------------------------------------
    # Evaluate current production performance
    # -----------------------------------------------------

    production = (
        calculate_active_performance(
            evaluated_dataset
        )
    )


    # -----------------------------------------------------
    # Calculate degradation
    # -----------------------------------------------------

    accuracy_drop = (
        baseline[
            "accuracy"
        ]
        -
        production[
            "accuracy"
        ]
    )


    precision_drop = (
        baseline[
            "precision"
        ]
        -
        production[
            "precision"
        ]
    )


    recall_drop = (
        baseline[
            "recall"
        ]
        -
        production[
            "recall"
        ]
    )


    f1_drop = (
        baseline[
            "f1"
        ]
        -
        production[
            "f1"
        ]
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
    # Autonomous healing decision
    # -----------------------------------------------------

    healing_required = (
        status
        ==
        "CRITICAL"
    )


    # -----------------------------------------------------
    # Human-readable reason
    # -----------------------------------------------------

    if healing_required:

        reason = (
            "Critical model performance degradation "
            "detected against the active champion baseline."
        )


    elif status == "WARNING":

        reason = (
            "Moderate degradation detected against "
            "the active champion baseline. "
            "Continue monitoring before retraining."
        )


    else:

        reason = (
            "Active model performance is within "
            "acceptable reliability thresholds."
        )


    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {

        "status":
            status,

        "healing_required":
            healing_required,

        "reason":
            reason,


        # -------------------------------------------------
        # Thresholds
        # -------------------------------------------------

        "thresholds": {

            "warning_drop":
                WARNING_DROP,

            "critical_drop":
                CRITICAL_DROP,
        },


        # -------------------------------------------------
        # Baseline metadata
        # -------------------------------------------------

        "baseline_metadata": {

            "source":
                active_baseline.get(
                    "source"
                ),

            "champion_version":
                active_baseline.get(
                    "champion_version"
                ),

            "previous_champion_version":
                active_baseline.get(
                    "previous_champion_version"
                ),

            "validation_type":
                active_baseline.get(
                    "validation_type"
                ),

            "validation_fraction":
                active_baseline.get(
                    "validation_fraction"
                ),
        },


        # -------------------------------------------------
        # Champion baseline
        # -------------------------------------------------

        "baseline": {

            "accuracy":
                baseline[
                    "accuracy"
                ],

            "precision":
                baseline[
                    "precision"
                ],

            "recall":
                baseline[
                    "recall"
                ],

            "f1":
                baseline[
                    "f1"
                ],
        },


        # -------------------------------------------------
        # Current production performance
        # -------------------------------------------------

        "production":
            production,


        # -------------------------------------------------
        # Degradation
        # -------------------------------------------------

        "degradation": {

            "accuracy_drop":
                float(
                    accuracy_drop
                ),

            "precision_drop":
                float(
                    precision_drop
                ),

            "recall_drop":
                float(
                    recall_drop
                ),

            "f1_drop":
                float(
                    f1_drop
                ),
        },


        # -------------------------------------------------
        # Dataset used
        # -------------------------------------------------

        "evaluation": {

            "dataset_path":
                str(
                    evaluated_dataset
                ),
        },
    }