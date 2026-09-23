from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "fraud_model.joblib"
)


BASELINE_METRICS_FILE = (
    PROJECT_ROOT
    / "models"
    / "baseline_metrics.json"
)


PRODUCTION_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)


# ---------------------------------------------------------
# 2. PREPARE DATA
# ---------------------------------------------------------

def prepare_data(data):

    X = data.drop(
        columns=[
            "transaction_id",
            "is_fraud",
        ]
    )

    y = data[
        "is_fraud"
    ]

    return X, y


# ---------------------------------------------------------
# 3. LOAD BASELINE METRICS
# ---------------------------------------------------------

def load_baseline_metrics():

    with open(
        BASELINE_METRICS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        metrics = json.load(
            file
        )

    return metrics


# ---------------------------------------------------------
# 4. CALCULATE CURRENT PERFORMANCE
# ---------------------------------------------------------

def calculate_metrics(
    model,
    X,
    y,
):

    predictions = model.predict(
        X
    )


    accuracy = accuracy_score(
        y,
        predictions,
    )


    precision = precision_score(
        y,
        predictions,
        zero_division=0,
    )


    recall = recall_score(
        y,
        predictions,
        zero_division=0,
    )


    f1 = f1_score(
        y,
        predictions,
        zero_division=0,
    )


    matrix = confusion_matrix(
        y,
        predictions,
    )


    return {
        "accuracy": float(
            accuracy
        ),
        "precision": float(
            precision
        ),
        "recall": float(
            recall
        ),
        "f1": float(
            f1
        ),
        "confusion_matrix": (
            matrix
        ),
    }


# ---------------------------------------------------------
# 5. PERFORMANCE DROP
# ---------------------------------------------------------

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
            - production_value
        )


        drop_report[
            metric
        ] = float(
            difference
        )


    return drop_report


# ---------------------------------------------------------
# 6. DETERMINE MODEL STATUS
# ---------------------------------------------------------

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
        or recall_drop >= 0.15
    ):

        return "CRITICAL"


    elif (
        f1_drop >= 0.05
        or recall_drop >= 0.05
    ):

        return "WARNING"


    return "HEALTHY"


# ---------------------------------------------------------
# 7. MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print(
        "\nLoading trained model..."
    )


    model = joblib.load(
        MODEL_FILE
    )


    print(
        "Model loaded successfully."
    )


    print(
        "\nLoading saved baseline metrics..."
    )


    baseline_metrics = (
        load_baseline_metrics()
    )


    print(
        "Baseline metrics loaded successfully."
    )


    print(
        "\nLoading production dataset..."
    )


    production_data = pd.read_csv(
        PRODUCTION_DATA_FILE
    )


    print(
        "Production dataset loaded successfully."
    )


    X_production, y_production = (
        prepare_data(
            production_data
        )
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


    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    print("\n")
    print("=" * 70)

    print(
        "MODEL PERFORMANCE REPORT"
    )

    print("=" * 70)


    print(
        "\nBASELINE PERFORMANCE"
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
        "\nPRODUCTION PERFORMANCE"
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
        "\nMODEL STATUS:"
    )

    print(
        status
    )


    print(
        "\nProduction Confusion Matrix:"
    )

    print(
        production_metrics[
            "confusion_matrix"
        ]
    )


    print("\n")
    print("=" * 70)


if __name__ == "__main__":
    main()