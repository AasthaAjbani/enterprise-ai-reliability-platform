from pathlib import Path

import joblib
import pandas as pd

from app.monitoring.data_quality_monitor import (
    check_missing_columns,
    check_missing_values,
    check_duplicates,
    check_numerical_rules,
    check_categorical_rules,
    calculate_quality_score,
    determine_quality_status,
)

from app.monitoring.drift_detector import (
    generate_drift_report,
    calculate_overall_status,
)

from app.monitoring.performance_monitor import (
    prepare_data,
    calculate_metrics,
    calculate_performance_drop,
    determine_model_status,
    load_baseline_metrics,
)

from app.monitoring.root_cause_analyzer import (
    get_feature_importance,
    generate_root_cause_report,
    generate_recommendation,
)

from app.monitoring.anomaly_detector import (
    train_anomaly_detector,
    detect_anomalies,
    generate_anomaly_summary,
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
# 2. DATA QUALITY ANALYSIS
# ---------------------------------------------------------

def run_data_quality_analysis(data):

    missing_columns = (
        check_missing_columns(
            data
        )
    )


    if missing_columns:

        return {
            "status": "CRITICAL",
            "score": 0,
            "missing_columns": missing_columns,
            "missing_values": {},
            "duplicates": 0,
            "numerical_issues": {},
            "categorical_issues": {},
        }


    missing_values = (
        check_missing_values(
            data
        )
    )


    duplicates = (
        check_duplicates(
            data
        )
    )


    numerical_issues = (
        check_numerical_rules(
            data
        )
    )


    categorical_issues = (
        check_categorical_rules(
            data
        )
    )


    quality_score = (
        calculate_quality_score(
            len(data),
            missing_values,
            duplicates,
            numerical_issues,
            categorical_issues,
        )
    )


    status = (
        determine_quality_status(
            quality_score,
            missing_columns,
        )
    )


    return {
        "status": status,
        "score": quality_score,
        "missing_columns": missing_columns,
        "missing_values": missing_values,
        "duplicates": duplicates,
        "numerical_issues": numerical_issues,
        "categorical_issues": categorical_issues,
    }


# ---------------------------------------------------------
# 3. PERFORMANCE ANALYSIS
# ---------------------------------------------------------

def run_performance_analysis(
    model,
    production_data,
):

    baseline_metrics = (
        load_baseline_metrics()
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


    return {
        "status": status,
        "reference_metrics": baseline_metrics,
        "production_metrics": production_metrics,
        "performance_drop": performance_drop,
    }


# ---------------------------------------------------------
# 4. ANOMALY DETECTION ANALYSIS
# ---------------------------------------------------------

def run_anomaly_analysis(
    reference_data,
    production_data,
):

    detector, scaler = (
        train_anomaly_detector(
            reference_data
        )
    )


    anomaly_results = (
        detect_anomalies(
            detector,
            scaler,
            production_data,
        )
    )


    anomaly_report = (
        generate_anomaly_summary(
            anomaly_results
        )
    )


    return anomaly_report


# ---------------------------------------------------------
# 5. OVERALL SYSTEM STATUS
# ---------------------------------------------------------

def determine_overall_status(
    quality_status,
    drift_status,
    performance_status,
    anomaly_status,
):

    statuses = [
        quality_status,
        drift_status,
        performance_status,
        anomaly_status,
    ]


    if "CRITICAL" in statuses:

        return "CRITICAL"


    if "WARNING" in statuses:

        return "WARNING"


    return "HEALTHY"


# ---------------------------------------------------------
# 6. GENERATE COMPLETE RELIABILITY REPORT
# ---------------------------------------------------------

def generate_reliability_report():

    print(
        "\nLoading model and datasets..."
    )


    model = joblib.load(
        MODEL_FILE
    )


    reference_data = pd.read_csv(
        REFERENCE_DATA_FILE
    )


    production_data = pd.read_csv(
        PRODUCTION_DATA_FILE
    )


    print(
        "Model and datasets loaded successfully."
    )


    # -----------------------------------------------------
    # DATA QUALITY
    # -----------------------------------------------------

    quality_report = (
        run_data_quality_analysis(
            production_data
        )
    )


    # -----------------------------------------------------
    # DATA DRIFT
    # -----------------------------------------------------

    drift_report = (
        generate_drift_report(
            reference_data,
            production_data,
        )
    )


    drift_status = (
        calculate_overall_status(
            drift_report
        )
    )


    # -----------------------------------------------------
    # MODEL PERFORMANCE
    # -----------------------------------------------------

    performance_report = (
        run_performance_analysis(
            model,
            production_data,
        )
    )


    # -----------------------------------------------------
    # ANOMALY DETECTION
    # -----------------------------------------------------

    anomaly_report = (
        run_anomaly_analysis(
            reference_data,
            production_data,
        )
    )


    # -----------------------------------------------------
    # FEATURE IMPORTANCE
    # -----------------------------------------------------

    importance_report = (
        get_feature_importance(
            model
        )
    )


    # -----------------------------------------------------
    # ROOT CAUSE ANALYSIS
    # -----------------------------------------------------

    root_cause_report = (
        generate_root_cause_report(
            drift_report,
            importance_report,
        )
    )


    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    recommendation = (
        generate_recommendation(
            root_cause_report
        )
    )


    # -----------------------------------------------------
    # OVERALL STATUS
    # -----------------------------------------------------

    overall_status = (
        determine_overall_status(
            quality_report[
                "status"
            ],
            drift_status,
            performance_report[
                "status"
            ],
            anomaly_report[
                "status"
            ],
        )
    )


    return {
        "overall_status":
            overall_status,

        "data_quality":
            quality_report,

        "data_drift": {
            "status":
                drift_status,

            "report":
                drift_report,
        },

        "model_performance":
            performance_report,

        "anomaly_detection":
            anomaly_report,

        "root_cause":
            root_cause_report,

        "recommendation":
            recommendation,
    }


# ---------------------------------------------------------
# 7. PRINT COMPLETE REPORT
# ---------------------------------------------------------

def print_reliability_report(
    report,
):

    print("\n")
    print("=" * 80)

    print(
        "ENTERPRISE AI RELIABILITY REPORT"
    )

    print("=" * 80)


    # -----------------------------------------------------
    # OVERALL STATUS
    # -----------------------------------------------------

    print(
        f"\nOVERALL STATUS: "
        f"{report['overall_status']}"
    )


    # -----------------------------------------------------
    # SYSTEM HEALTH
    # -----------------------------------------------------

    print(
        "\nSYSTEM HEALTH"
    )


    print(
        f"Data Quality     : "
        f"{report['data_quality']['status']}"
    )


    print(
        f"Data Drift       : "
        f"{report['data_drift']['status']}"
    )


    print(
        f"Model Performance: "
        f"{report['model_performance']['status']}"
    )


    print(
        f"Anomaly Detection: "
        f"{report['anomaly_detection']['status']}"
    )


    # -----------------------------------------------------
    # DATA QUALITY
    # -----------------------------------------------------

    print("\n")
    print("-" * 80)

    print(
        "DATA QUALITY"
    )

    print("-" * 80)


    print(
        f"Quality Score: "
        f"{report['data_quality']['score']}/100"
    )


    print(
        f"Duplicate IDs: "
        f"{report['data_quality']['duplicates']}"
    )


    # -----------------------------------------------------
    # DRIFT
    # -----------------------------------------------------

    print("\n")
    print("-" * 80)

    print(
        "DATA DRIFT"
    )

    print("-" * 80)


    drift_columns = [
        "feature",
        "feature_type",
        "drift_level",
        "score",
    ]


    print(
        report[
            "data_drift"
        ][
            "report"
        ][
            drift_columns
        ].to_string(
            index=False
        )
    )


    # -----------------------------------------------------
    # PERFORMANCE
    # -----------------------------------------------------

    print("\n")
    print("-" * 80)

    print(
        "MODEL PERFORMANCE"
    )

    print("-" * 80)


    baseline_metrics = (
        report[
            "model_performance"
        ][
            "reference_metrics"
        ]
    )


    production_metrics = (
        report[
            "model_performance"
        ][
            "production_metrics"
        ]
    )


    print(
        "\nBaseline:"
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
        "\nProduction:"
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


    # -----------------------------------------------------
    # ANOMALY DETECTION
    # -----------------------------------------------------

    print("\n")
    print("-" * 80)

    print(
        "ANOMALY DETECTION"
    )

    print("-" * 80)


    anomaly_report = (
        report[
            "anomaly_detection"
        ]
    )


    print(
        f"Status              : "
        f"{anomaly_report['status']}"
    )

    print(
        f"Transactions        : "
        f"{anomaly_report['total_transactions']}"
    )

    print(
        f"Anomalies           : "
        f"{anomaly_report['anomaly_count']}"
    )

    print(
        f"Anomaly Percentage  : "
        f"{anomaly_report['anomaly_percentage']}%"
    )


    # -----------------------------------------------------
    # ROOT CAUSE
    # -----------------------------------------------------

    print("\n")
    print("-" * 80)

    print(
        "TOP ROOT CAUSES"
    )

    print("-" * 80)


    top_causes = (
        report[
            "root_cause"
        ]
        .head(5)
    )


    for _, row in (
        top_causes.iterrows()
    ):

        print(
            f"{row['feature']:<35} "
            f"Drift="
            f"{row['drift_level']:<10} "
            f"Priority="
            f"{row['root_cause_priority']}"
        )


    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    print("\n")
    print("-" * 80)

    print(
        "RECOMMENDATION"
    )

    print("-" * 80)


    print(
        report[
            "recommendation"
        ]
    )


    print("\n")
    print("=" * 80)


# ---------------------------------------------------------
# 8. MAIN
# ---------------------------------------------------------

def main():

    report = (
        generate_reliability_report()
    )


    print_reliability_report(
        report
    )


if __name__ == "__main__":
    main()