from pathlib import Path

import numpy as np
import pandas as pd

from scipy.stats import ks_2samp


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
# 2. FEATURE TYPES
# ---------------------------------------------------------

NUMERICAL_FEATURES = [
    "customer_age",
    "transaction_amount",
    "transaction_hour",
    "account_age_days",
    "previous_transactions",
    "failed_transactions_last_24h",
    "is_international",
]


CATEGORICAL_FEATURES = [
    "payment_method",
    "device_type",
    "customer_location",
]


# ---------------------------------------------------------
# 3. NUMERICAL DRIFT
# ---------------------------------------------------------

def detect_numerical_drift(
    reference_series,
    production_series,
):
    """
    Detect drift between two numerical distributions
    using the Kolmogorov-Smirnov test.
    """

    reference_series = reference_series.dropna()
    production_series = production_series.dropna()

    statistic, p_value = ks_2samp(
        reference_series,
        production_series,
    )

    if p_value < 0.01 and statistic >= 0.20:
        drift_level = "HIGH"

    elif p_value < 0.05 and statistic >= 0.10:
        drift_level = "MODERATE"

    else:
        drift_level = "LOW"

    return {
        "ks_statistic": round(float(statistic), 4),
        "p_value": round(float(p_value), 6),
        "drift_level": drift_level,
    }


# ---------------------------------------------------------
# 4. CATEGORICAL DRIFT
# ---------------------------------------------------------

def detect_categorical_drift(
    reference_series,
    production_series,
):
    """
    Compare category distributions using
    Total Variation Distance.
    """

    reference_distribution = (
        reference_series
        .value_counts(normalize=True)
    )

    production_distribution = (
        production_series
        .value_counts(normalize=True)
    )


    # Combine categories from both datasets
    all_categories = (
        reference_distribution.index
        .union(production_distribution.index)
    )


    reference_distribution = (
        reference_distribution
        .reindex(
            all_categories,
            fill_value=0,
        )
    )

    production_distribution = (
        production_distribution
        .reindex(
            all_categories,
            fill_value=0,
        )
    )


    # Total Variation Distance
    distance = 0.5 * np.abs(
        reference_distribution
        - production_distribution
    ).sum()


    if distance >= 0.20:
        drift_level = "HIGH"

    elif distance >= 0.10:
        drift_level = "MODERATE"

    else:
        drift_level = "LOW"


    return {
        "distance": round(float(distance), 4),
        "drift_level": drift_level,
    }


# ---------------------------------------------------------
# 5. CREATE COMPLETE DRIFT REPORT
# ---------------------------------------------------------

def generate_drift_report(
    reference_data,
    production_data,
):
    report = []


    # Numerical features
    for feature in NUMERICAL_FEATURES:

        result = detect_numerical_drift(
            reference_data[feature],
            production_data[feature],
        )

        report.append(
            {
                "feature": feature,
                "feature_type": "numerical",
                "drift_level": result[
                    "drift_level"
                ],
                "score": result[
                    "ks_statistic"
                ],
                "p_value": result[
                    "p_value"
                ],
            }
        )


    # Categorical features
    for feature in CATEGORICAL_FEATURES:

        result = detect_categorical_drift(
            reference_data[feature],
            production_data[feature],
        )

        report.append(
            {
                "feature": feature,
                "feature_type": "categorical",
                "drift_level": result[
                    "drift_level"
                ],
                "score": result[
                    "distance"
                ],
                "p_value": None,
            }
        )


    return pd.DataFrame(report)


# ---------------------------------------------------------
# 6. OVERALL DRIFT STATUS
# ---------------------------------------------------------

def calculate_overall_status(
    drift_report,
):
    high_count = (
        drift_report["drift_level"]
        == "HIGH"
    ).sum()

    moderate_count = (
        drift_report["drift_level"]
        == "MODERATE"
    ).sum()


    if high_count >= 2:
        return "CRITICAL"

    if high_count == 1 or moderate_count >= 2:
        return "WARNING"

    return "HEALTHY"


# ---------------------------------------------------------
# 7. MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print(
        "\nLoading reference and production data..."
    )


    reference_data = pd.read_csv(
        REFERENCE_DATA_FILE
    )

    production_data = pd.read_csv(
        PRODUCTION_DATA_FILE
    )


    print("Datasets loaded successfully.")


    drift_report = generate_drift_report(
        reference_data,
        production_data,
    )


    overall_status = calculate_overall_status(
        drift_report
    )


    print("\n")
    print("=" * 70)
    print("DATA DRIFT REPORT")
    print("=" * 70)


    print(
        drift_report.to_string(
            index=False
        )
    )


    print("\n")
    print("=" * 70)

    print(
        f"OVERALL DRIFT STATUS: {overall_status}"
    )

    print("=" * 70)


    high_drift_features = drift_report[
        drift_report["drift_level"]
        == "HIGH"
    ]


    if not high_drift_features.empty:

        print(
            "\nHigh drift detected in:"
        )

        for feature in high_drift_features[
            "feature"
        ]:

            print(
                f" - {feature}"
            )


if __name__ == "__main__":
    main()