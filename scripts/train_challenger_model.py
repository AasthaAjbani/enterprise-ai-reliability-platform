from __future__ import annotations

import json
import os
from pathlib import Path

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

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


REFERENCE_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "transactions_reference.csv"
)


DEFAULT_PRODUCTION_DATA_PATH = (
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
# RESOLVE PRODUCTION DATASET
# =========================================================

def resolve_production_data_path() -> Path:

    """
    Resolve the production dataset used for self-healing.

    Priority:

    1. HEALING_PRODUCTION_DATA environment variable
    2. Default transactions_production.csv
    """

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
    +
    NUMERICAL_FEATURES
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

    print(
        "\nLoading datasets..."
    )


    production_data_path = (
        resolve_production_data_path()
    )


    # -----------------------------------------------------
    # Validate files
    # -----------------------------------------------------

    if not REFERENCE_DATA_PATH.exists():

        raise FileNotFoundError(
            "Reference dataset not found:\n"
            f"{REFERENCE_DATA_PATH}"
        )


    if not production_data_path.exists():

        raise FileNotFoundError(
            "Production dataset not found:\n"
            f"{production_data_path}"
        )


    if not CURRENT_MODEL_PATH.exists():

        raise FileNotFoundError(
            "Current production model not found:\n"
            f"{CURRENT_MODEL_PATH}"
        )


    # -----------------------------------------------------
    # Load
    # -----------------------------------------------------

    reference_data = pd.read_csv(
        REFERENCE_DATA_PATH
    )


    production_data = pd.read_csv(
        production_data_path
    )


    # -----------------------------------------------------
    # Information
    # -----------------------------------------------------

    print(
        "\nProduction dataset:"
    )

    print(
        production_data_path
    )


    print(
        f"\nReference rows: "
        f"{len(reference_data)}"
    )


    print(
        f"Production rows: "
        f"{len(production_data)}"
    )


    return (
        reference_data,
        production_data,
        production_data_path,
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
        +
        [
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
                f"is missing required columns: "
                f"{missing_columns}"
            )


    # -----------------------------------------------------
    # Validate production labels
    # -----------------------------------------------------

    production_labels = set(
        production_data[
            TARGET_COLUMN
        ]
        .dropna()
        .unique()
    )


    if not production_labels.issubset(
        {0, 1}
    ):

        raise ValueError(
            "Production labels must contain "
            "only 0 and 1."
        )


    if len(
        production_labels
    ) < 2:

        raise ValueError(
            "Production dataset must contain "
            "both fraud and non-fraud examples."
        )


# =========================================================
# PREPARE TRAINING DATA
# =========================================================

def prepare_training_data(
    reference_data,
    production_data,
):

    # -----------------------------------------------------
    # Historical training data
    #
    # Recreate the same 80% reference split used by
    # the original model-training process.
    # -----------------------------------------------------

    reference_train, _ = (
        train_test_split(
            reference_data,
            test_size=0.20,
            random_state=42,
            stratify=reference_data[
                TARGET_COLUMN
            ],
        )
    )


    # -----------------------------------------------------
    # NEW PRODUCTION BATCH
    #
    # 70% = challenger training
    # 30% = completely untouched validation
    #
    # Current champion and challenger will BOTH be tested
    # on exactly the same 30%.
    # -----------------------------------------------------

    (
        production_train,
        production_validation,
    ) = train_test_split(

        production_data,

        test_size=0.30,

        random_state=42,

        stratify=production_data[
            TARGET_COLUMN
        ],
    )


    # -----------------------------------------------------
    # Challenger training data
    # -----------------------------------------------------

    challenger_training_data = (
        pd.concat(
            [
                reference_train,
                production_train,
            ],
            ignore_index=True,
        )
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


    # -----------------------------------------------------
    # Untouched validation data
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Information
    # -----------------------------------------------------

    print(
        "\nTraining / validation split"
    )

    print(
        "---------------------------"
    )


    print(
        "Historical training rows:",
        len(
            reference_train
        ),
    )


    print(
        "Recent production training rows:",
        len(
            production_train
        ),
    )


    print(
        "Total challenger training rows:",
        len(
            challenger_training_data
        ),
    )


    print(
        "Untouched production validation rows:",
        len(
            production_validation
        ),
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

    preprocessor = (
        ColumnTransformer(
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
    )


    classifier = (
        RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
    )


    challenger = (
        Pipeline(
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
    )


    return challenger


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
# PROMOTION DECISION
# =========================================================

def evaluate_promotion(
    current_metrics,
    challenger_metrics,
):

    f1_improvement = (
        challenger_metrics[
            "f1"
        ]
        -
        current_metrics[
            "f1"
        ]
    )


    recall_improvement = (
        challenger_metrics[
            "recall"
        ]
        -
        current_metrics[
            "recall"
        ]
    )


    precision_change = (
        challenger_metrics[
            "precision"
        ]
        -
        current_metrics[
            "precision"
        ]
    )


    # -----------------------------------------------------
    # Promotion checks
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
            bool(
                promotion_eligible
            ),

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
                bool(
                    f1_pass
                ),

            "recall_pass":
                bool(
                    recall_pass
                ),

            "precision_pass":
                bool(
                    precision_pass
                ),
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
        "-" * len(
            title
        )
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
# SAVE CHALLENGER
# =========================================================

def save_challenger(
    challenger_model,
):

    CHALLENGER_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    joblib.dump(
        challenger_model,
        CHALLENGER_MODEL_PATH,
    )


    print(
        "\nChallenger model saved:"
    )

    print(
        CHALLENGER_MODEL_PATH
    )


# =========================================================
# SAVE COMPARISON REPORT
# =========================================================

def save_comparison_report(
    decision,
    current_metrics,
    challenger_metrics,
    promotion,
    production_data_path,
):

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

            "production_data_path":
                str(
                    production_data_path
                ),

            "production_validation_fraction":
                0.30,

            "production_training_fraction":
                0.70,

            "random_state":
                42,

            "comparison_note":
                (
                    "Current champion and challenger "
                    "were evaluated on the same untouched "
                    "production validation set."
                ),
        },


        "training_strategy": {

            "historical_source":
                str(
                    REFERENCE_DATA_PATH
                ),

            "recent_production_source":
                str(
                    production_data_path
                ),

            "challenger_training_note":
                (
                    "Challenger was trained using the "
                    "historical reference training split "
                    "plus 70 percent of the new "
                    "production batch."
                ),
        },
    }


    with COMPARISON_REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
        )


    print(
        "\nComparison report saved:"
    )

    print(
        COMPARISON_REPORT_PATH
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
        "CHALLENGER MODEL TRAINING"
    )

    print(
        "=" * 60
    )


    # -----------------------------------------------------
    # Load data
    # -----------------------------------------------------

    (
        reference_data,
        production_data,
        production_data_path,
    ) = load_data()


    # -----------------------------------------------------
    # Validate
    # -----------------------------------------------------

    validate_data(
        reference_data,
        production_data,
    )


    # -----------------------------------------------------
    # Prepare train + untouched validation
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
    # Load current champion
    # -----------------------------------------------------

    print(
        "\nLoading current deployed model..."
    )


    current_model = (
        joblib.load(
            CURRENT_MODEL_PATH
        )
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
    # Fair evaluation
    #
    # Both models see exactly the same untouched
    # Batch 2 validation set.
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
    # Promotion quality gate
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
        f"F1 improvement     : "
        f"{promotion['f1_improvement']:+.4f}"
    )


    print(
        f"Recall improvement : "
        f"{promotion['recall_improvement']:+.4f}"
    )


    print(
        f"Precision change   : "
        f"{promotion['precision_change']:+.4f}"
    )


    # -----------------------------------------------------
    # Decision
    # -----------------------------------------------------

    if promotion[
        "promotion_eligible"
    ]:

        decision = (
            "CHALLENGER_ELIGIBLE_FOR_PROMOTION"
        )

        print()
        print(
            "RESULT: Challenger passed "
            "promotion criteria."
        )


    else:

        decision = (
            "KEEP_CURRENT_MODEL"
        )

        print()
        print(
            "RESULT: Challenger failed "
            "promotion criteria."
        )


    # -----------------------------------------------------
    # Save challenger regardless of decision
    #
    # Promotion script will decide whether it becomes
    # the active model.
    # -----------------------------------------------------

    save_challenger(
        challenger_model
    )


    # -----------------------------------------------------
    # Save comparison report
    # -----------------------------------------------------

    save_comparison_report(
        decision,
        current_metrics,
        challenger_metrics,
        promotion,
        production_data_path,
    )


    print()
    print(
        "=" * 60
    )

    print(
        "CHALLENGER TRAINING COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        f"\nDecision: "
        f"{decision}"
    )

    print()


# =========================================================
# EXECUTE
# =========================================================

if __name__ == "__main__":
    main()