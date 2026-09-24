from pathlib import Path
import hashlib
import json

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

PRODUCTION_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
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
    + NUMERICAL_FEATURES
)


# =========================================================
# HASH FILE
# =========================================================

def calculate_sha256(
    path: Path,
):

    sha256 = hashlib.sha256()


    with open(
        path,
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
# LOAD DEPLOYMENT STATE
# =========================================================

def load_deployment_state():

    if not DEPLOYMENT_STATE_PATH.exists():

        raise FileNotFoundError(
            "\nDeployment state not found:\n"
            f"{DEPLOYMENT_STATE_PATH}"
        )


    with open(
        DEPLOYMENT_STATE_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# CALCULATE METRICS
# =========================================================

def calculate_metrics(
    model,
    X,
    y,
):

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

    print(
        "\n"
        "=============================================="
    )

    print(
        " ENTERPRISE AI RELIABILITY PLATFORM"
    )

    print(
        " PROMOTION VERIFICATION"
    )

    print(
        "=============================================="
    )


    # =====================================================
    # CHECK FILES
    # =====================================================

    required_files = [
        ACTIVE_MODEL_PATH,
        CHALLENGER_MODEL_PATH,
        DEPLOYMENT_STATE_PATH,
        PRODUCTION_DATA_PATH,
    ]


    for path in required_files:

        if not path.exists():

            raise FileNotFoundError(
                f"\nRequired file missing:\n{path}"
            )


    # =====================================================
    # DEPLOYMENT STATE
    # =====================================================

    state = (
        load_deployment_state()
    )


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
        state[
            "champion_version"
        ]
    )


    print(
        "\nPrevious champion:"
    )

    print(
        state[
            "previous_champion_version"
        ]
    )


    print(
        "\nRollback available:"
    )

    print(
        state[
            "rollback_available"
        ]
    )


    print(
        "\nPromoted at:"
    )

    print(
        state[
            "promoted_at"
        ]
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
            "\nActive production model does not "
            "match the promoted challenger."
        )


    # =====================================================
    # LOAD PRODUCTION DATA
    # =====================================================

    print(
        "\nLoading production data..."
    )


    production_data = pd.read_csv(
        PRODUCTION_DATA_PATH
    )


    print(
        "Production rows:"
    )

    print(
        len(
            production_data
        )
    )


    X = (
        production_data[
            FEATURE_COLUMNS
        ]
    )


    y = (
        production_data[
            TARGET_COLUMN
        ]
    )


    # =====================================================
    # LOAD ACTIVE MODEL
    # =====================================================

    print(
        "\nLoading active production model..."
    )


    active_model = (
        joblib.load(
            ACTIVE_MODEL_PATH
        )
    )


    # =====================================================
    # EVALUATE ACTIVE MODEL
    # =====================================================

    active_metrics = (
        calculate_metrics(
            active_model,
            X,
            y,
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
    # OPTIONAL: EVALUATE PREVIOUS CHAMPION
    # =====================================================

    backup_path_value = (
        state.get(
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
                    X,
                    y,
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
    # COMPARISON
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

    print(
        "\n=============================================="
    )

    print(
        " PROMOTION VERIFIED"
    )

    print(
        "=============================================="
    )


    print(
        "\nActive model artifact matches challenger."
    )


    print(
        "\nChampion version:"
    )

    print(
        state[
            "champion_version"
        ]
    )


    print(
        "\nThe self-healing deployment "
        "completed successfully."
    )


# =========================================================
# EXECUTE
# =========================================================

if __name__ == "__main__":
    main()