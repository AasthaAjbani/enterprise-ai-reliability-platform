from pathlib import Path

import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

REFERENCE_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "transactions_reference.csv"
)

PRODUCTION_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "transactions_production.csv"
)


# ---------------------------------------------------------
# 2. NUMERICAL FEATURES FOR ANOMALY DETECTION
# ---------------------------------------------------------

ANOMALY_FEATURES = [
    "customer_age",
    "transaction_amount",
    "transaction_hour",
    "account_age_days",
    "previous_transactions",
    "failed_transactions_last_24h",
    "is_international",
]


# ---------------------------------------------------------
# 3. TRAIN ANOMALY MODEL
# ---------------------------------------------------------

def train_anomaly_detector(reference_data):

    X_reference = reference_data[
        ANOMALY_FEATURES
    ].copy()

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X_reference
    )

    detector = IsolationForest(
        n_estimators=200,
        contamination=0.03,
        random_state=42,
        n_jobs=-1,
    )

    detector.fit(
        X_scaled
    )

    return detector, scaler


# ---------------------------------------------------------
# 4. DETECT PRODUCTION ANOMALIES
# ---------------------------------------------------------

def detect_anomalies(
    detector,
    scaler,
    production_data,
):

    X_production = production_data[
        ANOMALY_FEATURES
    ].copy()

    X_scaled = scaler.transform(
        X_production
    )

    predictions = detector.predict(
        X_scaled
    )

    anomaly_scores = detector.decision_function(
        X_scaled
    )

    result = production_data.copy()

    result["anomaly_prediction"] = predictions

    result["anomaly_score"] = anomaly_scores

    result["is_anomaly"] = (
        result["anomaly_prediction"] == -1
    )

    return result


# ---------------------------------------------------------
# 5. GENERATE ANOMALY SUMMARY
# ---------------------------------------------------------

def generate_anomaly_summary(
    anomaly_results,
):

    total_transactions = len(
        anomaly_results
    )

    anomaly_count = int(
        anomaly_results[
            "is_anomaly"
        ].sum()
    )

    anomaly_percentage = (
        anomaly_count
        / total_transactions
        * 100
    )


    if anomaly_percentage >= 10:

        status = "CRITICAL"

    elif anomaly_percentage >= 5:

        status = "WARNING"

    else:

        status = "HEALTHY"


    top_anomalies = (
        anomaly_results[
            anomaly_results[
                "is_anomaly"
            ]
        ]
        .sort_values(
            by="anomaly_score",
            ascending=True,
        )
        .head(10)
    )


    return {
        "status": status,
        "total_transactions": total_transactions,
        "anomaly_count": anomaly_count,
        "anomaly_percentage": round(
            anomaly_percentage,
            2,
        ),
        "top_anomalies": top_anomalies,
    }


# ---------------------------------------------------------
# 6. MAIN
# ---------------------------------------------------------

def main():

    print(
        "\nLoading reference data..."
    )

    reference_data = pd.read_csv(
        REFERENCE_DATA_FILE
    )


    print(
        "Loading production data..."
    )

    production_data = pd.read_csv(
        PRODUCTION_DATA_FILE
    )


    print(
        "Training anomaly detector..."
    )

    detector, scaler = (
        train_anomaly_detector(
            reference_data
        )
    )


    print(
        "Detecting anomalies..."
    )

    anomaly_results = (
        detect_anomalies(
            detector,
            scaler,
            production_data,
        )
    )


    summary = (
        generate_anomaly_summary(
            anomaly_results
        )
    )


    print("\n")
    print("=" * 80)

    print(
        "ANOMALY DETECTION REPORT"
    )

    print("=" * 80)


    print(
        f"\nStatus: "
        f"{summary['status']}"
    )


    print(
        f"Total transactions: "
        f"{summary['total_transactions']}"
    )


    print(
        f"Anomalies detected: "
        f"{summary['anomaly_count']}"
    )


    print(
        f"Anomaly percentage: "
        f"{summary['anomaly_percentage']}%"
    )


    print(
        "\nTop suspicious transactions:"
    )


    columns_to_show = [
        "transaction_id",
        "transaction_amount",
        "transaction_hour",
        "account_age_days",
        "failed_transactions_last_24h",
        "is_international",
        "anomaly_score",
    ]


    print(
        summary[
            "top_anomalies"
        ][
            columns_to_show
        ].to_string(
            index=False
        )
    )


    print("\n")
    print("=" * 80)


if __name__ == "__main__":
    main()