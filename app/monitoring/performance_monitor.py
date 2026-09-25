from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from sklearn.model_selection import (
    train_test_split,
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


MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "fraud_model.joblib"
)


DEFAULT_PRODUCTION_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)


TARGET_COLUMN = "is_fraud"


# =========================================================
# RESOLVE PRODUCTION DATASET
# =========================================================

def resolve_production_data_path(
    production_data_path: Path | None = None,
) -> Path:

    """
    Resolve the current production dataset.

    Priority:

    1. Explicit function argument
    2. HEALING_PRODUCTION_DATA environment variable
    3. Default production dataset
    """

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
        DEFAULT_PRODUCTION_DATA_FILE
        .resolve()
    )


# =========================================================
# PREPARE DATA
# =========================================================

def prepare_data(
    data: pd.DataFrame,
):

    X = data.drop(
        columns=[
            "transaction_id",
            TARGET_COLUMN,
        ]
    )


    y = data[
        TARGET_COLUMN
    ]


    return (
        X,
        y,
    )


# =========================================================
# LOAD ACTIVE CHAMPION BASELINE
# =========================================================

def load_baseline_metrics() -> dict[str, float]:

    active_baseline = (
        get_active_model_baseline()
    )


    return {
        "accuracy":
            float(
                active_baseline[
                    "metrics"
                ][
                    "accuracy"
                ]
            ),

        "precision":
            float(
                active_baseline[
                    "metrics"
                ][
                    "precision"
                ]
            ),

        "recall":
            float(
                active_baseline[
                    "metrics"
                ][
                    "recall"
                ]
            ),

        "f1":
            float(
                active_baseline[
                    "metrics"
                ][
                    "f1"
                ]
            ),
    }


# =========================================================
# BASELINE METADATA
# =========================================================

def load_baseline_metadata() -> dict[str, Any]:

    active_baseline = (
        get_active_model_baseline()
    )


    return {

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

        "production_data_path":
            active_baseline.get(
                "production_data_path"
            ),

        "random_state":
            active_baseline.get(
                "random_state"
            ),
    }


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


    accuracy = (
        accuracy_score(
            y,
            predictions,
        )
    )


    precision = (
        precision_score(
            y,
            predictions,
            zero_division=0,
        )
    )


    recall = (
        recall_score(
            y,
            predictions,
            zero_division=0,
        )
    )


    f1 = (
        f1_score(
            y,
            predictions,
            zero_division=0,
        )
    )


    matrix = (
        confusion_matrix(
            y,
            predictions,
        )
    )


    return {

        "accuracy":
            float(
                accuracy
            ),

        "precision":
            float(
                precision
            ),

        "recall":
            float(
                recall
            ),

        "f1":
            float(
                f1
            ),

        "confusion_matrix":
            matrix,
    }


# =========================================================
# PERFORMANCE DROP
# =========================================================

def calculate_performance_drop(
    reference_metrics,
    production_metrics,
):

    drop_report = {}


    for metric in [
        "accuracy",
        "precision",
        "recall",
        "f1",
    ]:

        reference_value = (
            reference_metrics[
                metric
            ]
        )


        production_value = (
            production_metrics[
                metric
            ]
        )


        difference = (
            reference_value
            -
            production_value
        )


        drop_report[
            metric
        ] = float(
            difference
        )


    return drop_report


# =========================================================
# DETERMINE MODEL STATUS
# =========================================================

def determine_model_status(
    performance_drop,
):

    f1_drop = (
        performance_drop[
            "f1"
        ]
    )


    recall_drop = (
        performance_drop[
            "recall"
        ]
    )


    if (
        f1_drop >= 0.15
        or
        recall_drop >= 0.15
    ):

        return "CRITICAL"


    if (
        f1_drop >= 0.05
        or
        recall_drop >= 0.05
    ):

        return "WARNING"


    return "HEALTHY"


# =========================================================
# PREPARE FAIR EVALUATION DATA
# =========================================================

def prepare_evaluation_data(
    production_data: pd.DataFrame,
    production_data_path: Path,
):

    """
    Decide how the active champion should be evaluated.

    When the selected production batch is the same batch
    that was used to create the champion, evaluate only on
    the same untouched validation split.

    For a future unseen production batch, evaluate the
    entire batch.
    """

    active_baseline = (
        get_active_model_baseline()
    )


    accepted_data_path = (
        active_baseline.get(
            "production_data_path"
        )
    )


    validation_fraction = (
        active_baseline.get(
            "validation_fraction"
        )
    )


    random_state = (
        active_baseline.get(
            "random_state"
        )
    )


    # -----------------------------------------------------
    # Default:
    # current dataset is unseen production.
    # -----------------------------------------------------

    evaluation_data = (
        production_data
    )


    evaluation_mode = (
        "full_production_batch"
    )


    # -----------------------------------------------------
    # If this is the same batch used during promotion,
    # recreate the untouched validation split.
    # -----------------------------------------------------

    if (
        accepted_data_path
        and
        validation_fraction is not None
    ):

        accepted_path = Path(
            accepted_data_path
        )


        if not accepted_path.is_absolute():

            accepted_path = (
                PROJECT_ROOT
                / accepted_path
            )


        accepted_path = (
            accepted_path.resolve()
        )


        current_path = (
            production_data_path.resolve()
        )


        if (
            accepted_path
            ==
            current_path
        ):

            split_random_state = (
                int(
                    random_state
                )
                if random_state is not None
                else 42
            )


            _, evaluation_data = (
                train_test_split(
                    production_data,
                    test_size=
                        float(
                            validation_fraction
                        ),
                    random_state=
                        split_random_state,
                    stratify=
                        production_data[
                            TARGET_COLUMN
                        ],
                )
            )


            evaluation_mode = (
                "held_out_production_validation"
            )


    return (
        evaluation_data,
        evaluation_mode,
    )


# =========================================================
# RUN PERFORMANCE ANALYSIS
# =========================================================

def run_performance_analysis(
    model,
    production_data: pd.DataFrame,
    production_data_path: Path | None = None,
):

    resolved_path = (
        resolve_production_data_path(
            production_data_path
        )
    )


    baseline_metrics = (
        load_baseline_metrics()
    )


    baseline_metadata = (
        load_baseline_metadata()
    )


    (
        evaluation_data,
        evaluation_mode,
    ) = prepare_evaluation_data(
        production_data,
        resolved_path,
    )


    (
        X_production,
        y_production,
    ) = prepare_data(
        evaluation_data
    )


    production_metrics = (
        calculate_metrics(
            model,
            X_production,
            y_production,
        )
    )


    performance_drop = (
        calculate_performance_drop(
            baseline_metrics,
            production_metrics,
        )
    )


    status = (
        determine_model_status(
            performance_drop
        )
    )


    return {

        "status":
            status,

        "reference_metrics":
            baseline_metrics,

        "production_metrics":
            production_metrics,

        "performance_drop":
            performance_drop,

        "baseline_metadata":
            baseline_metadata,

        "evaluation_metadata": {

            "dataset_path":
                str(
                    resolved_path
                ),

            "evaluation_mode":
                evaluation_mode,

            "evaluated_rows":
                int(
                    len(
                        evaluation_data
                    )
                ),
        },
    }


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\nLoading trained model..."
    )


    model = (
        joblib.load(
            MODEL_FILE
        )
    )


    print(
        "Model loaded successfully."
    )


    production_data_path = (
        resolve_production_data_path()
    )


    print(
        "\nProduction dataset:"
    )


    print(
        production_data_path
    )


    production_data = (
        pd.read_csv(
            production_data_path
        )
    )


    report = (
        run_performance_analysis(
            model,
            production_data,
            production_data_path,
        )
    )


    baseline_metrics = (
        report[
            "reference_metrics"
        ]
    )


    production_metrics = (
        report[
            "production_metrics"
        ]
    )


    performance_drop = (
        report[
            "performance_drop"
        ]
    )


    print()
    print(
        "=" * 70
    )

    print(
        "MODEL PERFORMANCE REPORT"
    )

    print(
        "=" * 70
    )


    print(
        "\nACTIVE CHAMPION BASELINE"
    )


    print(
        f"Accuracy : "
        f"{baseline_metrics['accuracy']:.4f}"
    )


    print(
        f"Precision: "
        f"{baseline_metrics['precision']:.4f}"
    )


    print(
        f"Recall   : "
        f"{baseline_metrics['recall']:.4f}"
    )


    print(
        f"F1 Score : "
        f"{baseline_metrics['f1']:.4f}"
    )


    print(
        "\nCURRENT PERFORMANCE"
    )


    print(
        f"Accuracy : "
        f"{production_metrics['accuracy']:.4f}"
    )


    print(
        f"Precision: "
        f"{production_metrics['precision']:.4f}"
    )


    print(
        f"Recall   : "
        f"{production_metrics['recall']:.4f}"
    )


    print(
        f"F1 Score : "
        f"{production_metrics['f1']:.4f}"
    )


    print(
        "\nPERFORMANCE DROP"
    )


    for metric, value in (
        performance_drop.items()
    ):

        print(
            f"{metric.capitalize():10}: "
            f"{value:.4f}"
        )


    print(
        "\nEvaluation mode:"
    )


    print(
        report[
            "evaluation_metadata"
        ][
            "evaluation_mode"
        ]
    )


    print(
        "\nEvaluated rows:"
    )


    print(
        report[
            "evaluation_metadata"
        ][
            "evaluated_rows"
        ]
    )


    print(
        "\nMODEL STATUS:"
    )


    print(
        report[
            "status"
        ]
    )


    print(
        "\nConfusion Matrix:"
    )


    print(
        production_metrics[
            "confusion_matrix"
        ]
    )


    print()
    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()