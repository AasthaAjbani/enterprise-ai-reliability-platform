from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REFERENCE_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "transactions_reference.csv"
)

PRODUCTION_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)

CURRENT_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "fraud_model.joblib"
)

CHALLENGER_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "challenger_fraud_model.joblib"
)

COMPARISON_REPORT_PATH = (
    PROJECT_ROOT
    / "models"
    / "challenger_comparison.json"
)


# =========================================================
# FEATURES
# =========================================================

TARGET_COLUMN = "is_fraud"

ID_COLUMN = "transaction_id"


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
# PROMOTION RULES
# =========================================================

MIN_F1_IMPROVEMENT = 0.05

MIN_RECALL_IMPROVEMENT = 0.00

MAX_PRECISION_DROP = 0.02


# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    print("\nLoading datasets...")

    reference_data = pd.read_csv(
        REFERENCE_DATA_PATH
    )

    production_data = pd.read_csv(
        PRODUCTION_DATA_PATH
    )

    print(
        f"Reference rows: {len(reference_data)}"
    )

    print(
        f"Production rows: {len(production_data)}"
    )

    return (
        reference_data,
        production_data,
    )


# =========================================================
# VALIDATE DATA
# =========================================================

def validate_data(
    reference_data,
    production_data,
):

    required_columns = (
        FEATURE_COLUMNS
        + [
            TARGET_COLUMN,
            ID_COLUMN,
        ]
    )


    for dataset_name, dataset in [
        (
            "reference",
            reference_data,
        ),
        (
            "production",
            production_data,
        ),
    ]:

        missing_columns = [
            column
            for column
            in required_columns
            if column
            not in dataset.columns
        ]


        if missing_columns:

            raise ValueError(
                f"{dataset_name} dataset "
                f"is missing columns: "
                f"{missing_columns}"
            )


    production_labels = set(
        production_data[
            TARGET_COLUMN
        ].dropna().unique()
    )


    if not production_labels.issubset(
        {0, 1}
    ):

        raise ValueError(
            "Production labels must "
            "contain only 0 and 1."
        )


# =========================================================
# PREPARE TRAINING DATA
# =========================================================

def prepare_training_data(
    reference_data,
    production_data,
):

    # -----------------------------------------------------
    # Recreate the SAME reference split used when the
    # original deployed model was trained.
    #
    # Current deployed model was trained on reference_train.
    # -----------------------------------------------------

    reference_train, _ = train_test_split(
        reference_data,
        test_size=0.20,
        random_state=42,
        stratify=reference_data[
            TARGET_COLUMN
        ],
    )


    # -----------------------------------------------------
    # Split CURRENT production labels.
    #
    # 70%:
    # Used to teach the challenger about recent behavior.
    #
    # 30%:
    # Completely untouched validation set.
    # BOTH models are evaluated on this same dataset.
    # -----------------------------------------------------

    production_train, production_validation = (
        train_test_split(
            production_data,
            test_size=0.30,
            random_state=42,
            stratify=production_data[
                TARGET_COLUMN
            ],
        )
    )


    # -----------------------------------------------------
    # Combine historical + recent labeled training data.
    # -----------------------------------------------------

    challenger_training_data = pd.concat(
        [
            reference_train,
            production_train,
        ],
        ignore_index=True,
    )


    X_train = (
        challenger_training_data[
            FEATURE_COLUMNS
        ]
    )

    y_train = (
        challenger_training_data[
            TARGET_COLUMN
        ]
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


    print(
        "\nTraining / validation split"
    )

    print(
        "Historical training rows:",
        len(reference_train),
    )

    print(
        "Recent production training rows:",
        len(production_train),
    )

    print(
        "Total challenger training rows:",
        len(challenger_training_data),
    )

    print(
        "Production validation rows:",
        len(production_validation),
    )


    return (
        X_train,
        y_train,
        X_validation,
        y_validation,
    )


# =========================================================
# BUILD CHALLENGER MODEL
# =========================================================

def build_challenger():

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "numerical",
                "passthrough",
                NUMERICAL_FEATURES,
            ),
        ]
    )


    classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )


    challenger = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "classifier",
                classifier,
            ),
        ]
    )


    return challenger


# =========================================================
# EVALUATION
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
        "accuracy": float(
            accuracy_score(
                y,
                predictions,
            )
        ),

        "precision": float(
            precision_score(
                y,
                predictions,
                zero_division=0,
            )
        ),

        "recall": float(
            recall_score(
                y,
                predictions,
                zero_division=0,
            )
        ),

        "f1": float(
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
# PROMOTION DECISION
# =========================================================

def evaluate_promotion(
    current_metrics,
    challenger_metrics,
):

    f1_improvement = (
        challenger_metrics["f1"]
        -
        current_metrics["f1"]
    )


    recall_improvement = (
        challenger_metrics["recall"]
        -
        current_metrics["recall"]
    )


    precision_change = (
        challenger_metrics["precision"]
        -
        current_metrics["precision"]
    )


    # -----------------------------------------------------
    # Promotion rules
    # -----------------------------------------------------

    f1_pass = (
        f1_improvement
        >=
        MIN_F1_IMPROVEMENT
    )


    recall_pass = (
        recall_improvement
        >=
        MIN_RECALL_IMPROVEMENT
    )


    precision_pass = (
        precision_change
        >=
        -MAX_PRECISION_DROP
    )


    promotion_eligible = (
        f1_pass
        and
        recall_pass
        and
        precision_pass
    )


    return {

        "promotion_eligible":
            promotion_eligible,

        "f1_improvement":
            float(
                f1_improvement
            ),

        "recall_improvement":
            float(
                recall_improvement
            ),

        "precision_change":
            float(
                precision_change
            ),

        "criteria": {

            "minimum_f1_improvement":
                MIN_F1_IMPROVEMENT,

            "minimum_recall_improvement":
                MIN_RECALL_IMPROVEMENT,

            "maximum_precision_drop":
                MAX_PRECISION_DROP,

            "f1_pass":
                f1_pass,

            "recall_pass":
                recall_pass,

            "precision_pass":
                precision_pass,
        },
    }


# =========================================================
# PRINT METRICS
# =========================================================

def print_metrics(
    title,
    metrics,
):

    print(
        f"\n{title}"
    )

    print(
        "-" * len(title)
    )

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
        " CHALLENGER MODEL TRAINING"
    )

    print(
        "=============================================="
    )


    # -----------------------------------------------------
    # Load
    # -----------------------------------------------------

    (
        reference_data,
        production_data,
    ) = load_data()


    validate_data(
        reference_data,
        production_data,
    )


    # -----------------------------------------------------
    # Prepare train + untouched production validation
    # -----------------------------------------------------

    (
        X_train,
        y_train,
        X_validation,
        y_validation,
    ) = prepare_training_data(
        reference_data,
        production_data,
    )


    # -----------------------------------------------------
    # Load current deployed model
    # -----------------------------------------------------

    print(
        "\nLoading current deployed model..."
    )

    current_model = joblib.load(
        CURRENT_MODEL_PATH
    )


    # -----------------------------------------------------
    # Train challenger
    # -----------------------------------------------------

    print(
        "\nTraining challenger model..."
    )


    challenger_model = (
        build_challenger()
    )


    challenger_model.fit(
        X_train,
        y_train,
    )


    print(
        "Challenger training complete."
    )


    # -----------------------------------------------------
    # FAIR COMPARISON
    #
    # BOTH models use SAME production validation set.
    # -----------------------------------------------------

    current_metrics = (
        calculate_metrics(
            current_model,
            X_validation,
            y_validation,
        )
    )


    challenger_metrics = (
        calculate_metrics(
            challenger_model,
            X_validation,
            y_validation,
        )
    )


    print_metrics(
        "CURRENT MODEL",
        current_metrics,
    )


    print_metrics(
        "CHALLENGER MODEL",
        challenger_metrics,
    )


    # -----------------------------------------------------
    # Promotion decision
    # -----------------------------------------------------

    promotion = (
        evaluate_promotion(
            current_metrics,
            challenger_metrics,
        )
    )


    print(
        "\nPROMOTION ANALYSIS"
    )

    print(
        "------------------"
    )

    print(
        f"F1 improvement: "
        f"{promotion['f1_improvement']:.4f}"
    )

    print(
        f"Recall improvement: "
        f"{promotion['recall_improvement']:.4f}"
    )

    print(
        f"Precision change: "
        f"{promotion['precision_change']:.4f}"
    )


    if (
        promotion[
            "promotion_eligible"
        ]
    ):

        decision = (
            "CHALLENGER_ELIGIBLE_FOR_PROMOTION"
        )

        print(
            "\n✅ Challenger passed "
            "promotion criteria."
        )

    else:

        decision = (
            "KEEP_CURRENT_MODEL"
        )

        print(
            "\n❌ Challenger did not pass "
            "all promotion criteria."
        )


    # -----------------------------------------------------
    # SAVE CHALLENGER
    #
    # IMPORTANT:
    # We DO NOT overwrite fraud_model.joblib.
    # -----------------------------------------------------

    joblib.dump(
        challenger_model,
        CHALLENGER_MODEL_PATH,
    )


    print(
        "\nSaved challenger model:"
    )

    print(
        CHALLENGER_MODEL_PATH
    )


    # -----------------------------------------------------
    # SAVE COMPARISON REPORT
    # -----------------------------------------------------

    report = {

        "decision":
            decision,

        "current_model":
            current_metrics,

        "challenger_model":
            challenger_metrics,

        "promotion_analysis":
            promotion,

        "validation_strategy": {
            "production_validation_fraction":
                0.30,

            "random_state":
                42,

            "comparison_note":
                (
                    "Current and challenger models "
                    "were evaluated on the same "
                    "held-out production validation set."
                ),
        },
    }


    with open(
        COMPARISON_REPORT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )


    print(
        "\nSaved comparison report:"
    )

    print(
        COMPARISON_REPORT_PATH
    )


    print(
        "\n=============================================="
    )

    print(
        f" FINAL DECISION: {decision}"
    )

    print(
        "=============================================="
    )


if __name__ == "__main__":
    main()