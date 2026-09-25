from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

ACTIVE_MODEL_PATH = (
    MODELS_DIR
    / "fraud_model.joblib"
)

CHALLENGER_MODEL_PATH = (
    MODELS_DIR
    / "challenger_fraud_model.joblib"
)

DEPLOYMENT_STATE_PATH = (
    MODELS_DIR
    / "deployment_state.json"
)

COMPARISON_REPORT_PATH = (
    MODELS_DIR
    / "challenger_comparison.json"
)

DEFAULT_PRODUCTION_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)


# =========================================================
# FEATURES
# =========================================================

TARGET_COLUMN = "is_fraud"


CATEGORICAL_FEATURES = [
    "payment_method",
    "device_type",
    "customer_location",
]


NUMERICAL_FEATURES = [
    "customer_age",
    "transaction_amount",
    "transaction_hour",
    "account_age_days",
    "previous_transactions",
    "failed_transactions_last_24h",
    "is_international",
]


FEATURE_COLUMNS = (
    CATEGORICAL_FEATURES
    +
    NUMERICAL_FEATURES
)


# =========================================================
# RESOLVE PRODUCTION DATASET
# =========================================================

def resolve_production_data_path(
    comparison: dict,
) -> Path:

    """
    Resolve the exact production dataset that was used
    during challenger training.

    Priority:

    1. challenger_comparison.json
    2. HEALING_PRODUCTION_DATA environment variable
    3. Default production dataset
    """

    validation_strategy = (
        comparison.get(
            "validation_strategy",
            {},
        )
    )


    if isinstance(
        validation_strategy,
        dict,
    ):

        saved_path = (
            validation_strategy.get(
                "production_data_path"
            )
        )


        if saved_path:

            path = Path(
                saved_path
            )


            if not path.is_absolute():

                path = (
                    PROJECT_ROOT
                    / path
                )


            return path.resolve()


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


    return (
        DEFAULT_PRODUCTION_DATA_PATH
        .resolve()
    )


# =========================================================
# HASH FILE
# =========================================================

def calculate_sha256(
    path: Path,
) -> str:

    sha256 = hashlib.sha256()


    with path.open(
        "rb",
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )


            if not chunk:

                break


            sha256.update(
                chunk
            )


    return sha256.hexdigest()


# =========================================================
# LOAD JSON
# =========================================================

def load_json(
    path: Path,
) -> dict:

    if not path.exists():

        raise FileNotFoundError(
            f"Required JSON file not found:\n"
            f"{path}"
        )


    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(
            file
        )


    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            f"Expected JSON object in:\n"
            f"{path}"
        )


    return data


# =========================================================
# CALCULATE METRICS
# =========================================================

def calculate_metrics(
    model,
    X,
    y,
):

    predictions = (
        model.predict(
            X
        )
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

        "confusion_matrix":
            confusion_matrix(
                y,
                predictions,
            ).tolist(),
    }


# =========================================================
# PRINT METRICS
# =========================================================

def print_metrics(
    metrics,
):

    print(
        f"Accuracy : "
        f"{metrics['accuracy']:.4f}"
    )


    print(
        f"Precision: "
        f"{metrics['precision']:.4f}"
    )


    print(
        f"Recall   : "
        f"{metrics['recall']:.4f}"
    )


    print(
        f"F1       : "
        f"{metrics['f1']:.4f}"
    )


    print(
        "Confusion Matrix:"
    )


    print(
        metrics[
            "confusion_matrix"
        ]
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "=" * 60
    )

    print(
        "ENTERPRISE AI RELIABILITY PLATFORM"
    )

    print(
        "PROMOTION VERIFICATION"
    )

    print(
        "=" * 60
    )


    # =====================================================
    # LOAD STATE + COMPARISON
    # =====================================================

    deployment_state = (
        load_json(
            DEPLOYMENT_STATE_PATH
        )
    )


    comparison = (
        load_json(
            COMPARISON_REPORT_PATH
        )
    )


    production_data_path = (
        resolve_production_data_path(
            comparison
        )
    )


    # =====================================================
    # CHECK FILES
    # =====================================================

    required_files = [
        ACTIVE_MODEL_PATH,
        CHALLENGER_MODEL_PATH,
        DEPLOYMENT_STATE_PATH,
        COMPARISON_REPORT_PATH,
        production_data_path,
    ]


    for path in required_files:

        if not path.exists():

            raise FileNotFoundError(
                "Required file missing:\n"
                f"{path}"
            )


    # =====================================================
    # DEPLOYMENT STATE
    # =====================================================

    print(
        "\nDEPLOYMENT STATE"
    )

    print(
        "----------------"
    )


    print(
        "Champion version:"
    )

    print(
        deployment_state[
            "champion_version"
        ]
    )


    print(
        "\nPrevious champion:"
    )

    print(
        deployment_state[
            "previous_champion_version"
        ]
    )


    print(
        "\nRollback available:"
    )

    print(
        deployment_state[
            "rollback_available"
        ]
    )


    print(
        "\nPromoted at:"
    )

    print(
        deployment_state[
            "promoted_at"
        ]
    )


    # =====================================================
    # VERIFY VERSION TRANSITION
    # =====================================================

    champion_version = str(
        deployment_state[
            "champion_version"
        ]
    )


    previous_version = str(
        deployment_state[
            "previous_champion_version"
        ]
    )


    if (
        champion_version
        ==
        previous_version
    ):

        raise RuntimeError(
            "Champion version and previous champion "
            "version cannot be identical after promotion."
        )


    print(
        "\nVersion transition:"
    )

    print(
        f"V{previous_version} -> "
        f"V{champion_version}"
    )


    # =====================================================
    # VERIFY ARTIFACT IDENTITY
    # =====================================================

    active_hash = (
        calculate_sha256(
            ACTIVE_MODEL_PATH
        )
    )


    challenger_hash = (
        calculate_sha256(
            CHALLENGER_MODEL_PATH
        )
    )


    print(
        "\nARTIFACT VERIFICATION"
    )

    print(
        "---------------------"
    )


    print(
        "Active model SHA256:"
    )

    print(
        active_hash
    )


    print(
        "\nChallenger SHA256:"
    )

    print(
        challenger_hash
    )


    artifact_match = (
        active_hash
        ==
        challenger_hash
    )


    print(
        "\nArtifact match:"
    )

    print(
        artifact_match
    )


    if not artifact_match:

        raise RuntimeError(
            "Active production model does not "
            "match the promoted challenger."
        )


    # =====================================================
    # PRODUCTION DATASET
    # =====================================================

    print(
        "\nVerification production dataset:"
    )

    print(
        production_data_path
    )


    production_data = (
        pd.read_csv(
            production_data_path
        )
    )


    print(
        "\nProduction rows:"
    )

    print(
        len(
            production_data
        )
    )


    # =====================================================
    # RECREATE UNTOUCHED VALIDATION SET
    # =====================================================

    validation_strategy = (
        comparison.get(
            "validation_strategy",
            {},
        )
    )


    validation_fraction = float(
        validation_strategy.get(
            "production_validation_fraction",
            0.30,
        )
    )


    random_state = int(
        validation_strategy.get(
            "random_state",
            42,
        )
    )


    _, production_validation = (
        train_test_split(
            production_data,
            test_size=
                validation_fraction,
            random_state=
                random_state,
            stratify=
                production_data[
                    TARGET_COLUMN
                ],
        )
    )


    print(
        "\nUntouched validation rows:"
    )

    print(
        len(
            production_validation
        )
    )


    X_validation = (
        production_validation[
            FEATURE_COLUMNS
        ]
    )


    y_validation = (
        production_validation[
            TARGET_COLUMN
        ]
    )


    # =====================================================
    # LOAD ACTIVE MODEL
    # =====================================================

    print(
        "\nLoading active champion..."
    )


    active_model = (
        joblib.load(
            ACTIVE_MODEL_PATH
        )
    )


    # =====================================================
    # EVALUATE ACTIVE CHAMPION
    # =====================================================

    active_metrics = (
        calculate_metrics(
            active_model,
            X_validation,
            y_validation,
        )
    )


    print(
        "\nACTIVE CHAMPION PERFORMANCE"
    )

    print(
        "---------------------------"
    )


    print_metrics(
        active_metrics
    )


    # =====================================================
    # CHECK AGAINST QUALITY-GATE METRICS
    # =====================================================

    expected_challenger_metrics = (
        comparison[
            "challenger_model"
        ]
    )


    metric_tolerance = 1e-12


    for metric_name in [
        "accuracy",
        "precision",
        "recall",
        "f1",
    ]:

        expected_value = float(
            expected_challenger_metrics[
                metric_name
            ]
        )


        actual_value = float(
            active_metrics[
                metric_name
            ]
        )


        if abs(
            expected_value
            -
            actual_value
        ) > metric_tolerance:

            raise RuntimeError(
                "Post-promotion validation metric "
                f"mismatch for {metric_name}. "
                f"Expected {expected_value}, "
                f"got {actual_value}."
            )


    print(
        "\nHeld-out metric verification:"
    )

    print(
        "PASSED"
    )


    # =====================================================
    # EVALUATE PREVIOUS CHAMPION
    # =====================================================

    backup_path_value = (
        deployment_state.get(
            "previous_model_backup"
        )
    )


    previous_metrics = None


    if backup_path_value:

        backup_path = Path(
            backup_path_value
        )


        if backup_path.exists():

            print(
                "\nLoading previous champion..."
            )


            previous_model = (
                joblib.load(
                    backup_path
                )
            )


            previous_metrics = (
                calculate_metrics(
                    previous_model,
                    X_validation,
                    y_validation,
                )
            )


            print(
                "\nPREVIOUS CHAMPION PERFORMANCE"
            )

            print(
                "-----------------------------"
            )


            print_metrics(
                previous_metrics
            )


    # =====================================================
    # PERFORMANCE CHANGE
    # =====================================================

    if previous_metrics:

        print(
            "\nPERFORMANCE CHANGE"
        )

        print(
            "------------------"
        )


        accuracy_change = (
            active_metrics[
                "accuracy"
            ]
            -
            previous_metrics[
                "accuracy"
            ]
        )


        precision_change = (
            active_metrics[
                "precision"
            ]
            -
            previous_metrics[
                "precision"
            ]
        )


        recall_change = (
            active_metrics[
                "recall"
            ]
            -
            previous_metrics[
                "recall"
            ]
        )


        f1_change = (
            active_metrics[
                "f1"
            ]
            -
            previous_metrics[
                "f1"
            ]
        )


        print(
            f"Accuracy change : "
            f"{accuracy_change:+.4f}"
        )


        print(
            f"Precision change: "
            f"{precision_change:+.4f}"
        )


        print(
            f"Recall change   : "
            f"{recall_change:+.4f}"
        )


        print(
            f"F1 change       : "
            f"{f1_change:+.4f}"
        )


    # =====================================================
    # SUCCESS
    # =====================================================

    print()
    print(
        "=" * 60
    )

    print(
        "PROMOTION VERIFIED"
    )

    print(
        "=" * 60
    )


    print(
        "\nActive model artifact matches "
        "the promoted challenger."
    )


    print(
        "\nHeld-out performance matches "
        "the quality-gate result."
    )


    print(
        "\nChampion version:"
    )

    print(
        champion_version
    )


    print(
        "\nPrevious champion version:"
    )

    print(
        previous_version
    )


    print(
        "\nRollback available:"
    )

    print(
        deployment_state[
            "rollback_available"
        ]
    )


# =========================================================
# EXECUTE
# =========================================================

if __name__ == "__main__":
    main()