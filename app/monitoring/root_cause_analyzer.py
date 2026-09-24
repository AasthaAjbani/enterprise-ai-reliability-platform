from pathlib import Path

import joblib
import pandas as pd

from app.monitoring.drift_detector import (
    generate_drift_report,
)


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

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
# 2. ORIGINAL MODEL FEATURES
# ---------------------------------------------------------

ORIGINAL_FEATURES = [
    "customer_age",
    "transaction_amount",
    "transaction_hour",
    "payment_method",
    "device_type",
    "customer_location",
    "account_age_days",
    "previous_transactions",
    "failed_transactions_last_24h",
    "is_international",
]


# ---------------------------------------------------------
# 3. EXTRACT FEATURE IMPORTANCE
# ---------------------------------------------------------

def get_feature_importance(pipeline):

    # -----------------------------------------------------
    # Get preprocessing step
    # -----------------------------------------------------

    if "preprocessor" not in pipeline.named_steps:

        raise KeyError(
            "Could not find 'preprocessor' step in pipeline. "
            f"Available steps: "
            f"{list(pipeline.named_steps.keys())}"
        )


    preprocessor = pipeline.named_steps[
        "preprocessor"
    ]


    # -----------------------------------------------------
    # Support both model pipeline versions
    #
    # V1:
    # preprocessor -> model
    #
    # V2 challenger:
    # preprocessor -> classifier
    # -----------------------------------------------------

    if "model" in pipeline.named_steps:

        model = pipeline.named_steps[
            "model"
        ]

    elif "classifier" in pipeline.named_steps:

        model = pipeline.named_steps[
            "classifier"
        ]

    else:

        raise KeyError(
            "Could not find model estimator in pipeline. "
            f"Available steps: "
            f"{list(pipeline.named_steps.keys())}"
        )


    # -----------------------------------------------------
    # Verify estimator supports feature importance
    # -----------------------------------------------------

    if not hasattr(
        model,
        "feature_importances_",
    ):

        raise AttributeError(
            "The active model does not expose "
            "'feature_importances_'. "
            f"Model type: {type(model).__name__}"
        )


    # -----------------------------------------------------
    # Get transformed feature names
    # -----------------------------------------------------

    transformed_feature_names = (
        preprocessor.get_feature_names_out()
    )


    # -----------------------------------------------------
    # Get transformed feature importance
    # -----------------------------------------------------

    transformed_importances = (
        model.feature_importances_
    )


    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    if (
        len(transformed_feature_names)
        !=
        len(transformed_importances)
    ):

        raise ValueError(
            "Feature-name count does not match "
            "model feature-importance count. "
            f"Feature names: "
            f"{len(transformed_feature_names)}, "
            f"Importances: "
            f"{len(transformed_importances)}"
        )


    # -----------------------------------------------------
    # Initialize original-feature importance map
    # -----------------------------------------------------

    importance_map = {
        feature: 0.0
        for feature in ORIGINAL_FEATURES
    }


    # -----------------------------------------------------
    # Map transformed features back to original features
    # -----------------------------------------------------

    for transformed_name, importance in zip(
        transformed_feature_names,
        transformed_importances,
    ):

        matched_feature = None


        # -------------------------------------------------
        # Numerical features
        #
        # Example:
        # numerical__transaction_amount
        # -------------------------------------------------

        for feature in ORIGINAL_FEATURES:

            numerical_name = (
                f"numerical__{feature}"
            )


            if (
                transformed_name
                ==
                numerical_name
            ):

                matched_feature = feature

                break


        # -------------------------------------------------
        # Categorical features
        #
        # Example:
        # categorical__payment_method_UPI
        # -------------------------------------------------

        if matched_feature is None:

            for feature in ORIGINAL_FEATURES:

                categorical_prefix = (
                    f"categorical__{feature}_"
                )


                if transformed_name.startswith(
                    categorical_prefix
                ):

                    matched_feature = feature

                    break


        # -------------------------------------------------
        # Aggregate one-hot encoded feature importance
        # back into the original feature
        # -------------------------------------------------

        if matched_feature is not None:

            importance_map[
                matched_feature
            ] += float(
                importance
            )


    # -----------------------------------------------------
    # Convert to DataFrame
    # -----------------------------------------------------

    importance_df = pd.DataFrame(
        {
            "feature": list(
                importance_map.keys()
            ),

            "model_importance": list(
                importance_map.values()
            ),
        }
    )


    return importance_df


# ---------------------------------------------------------
# 4. CREATE ROOT CAUSE REPORT
# ---------------------------------------------------------

def generate_root_cause_report(
    drift_report,
    importance_report,
):

    report = drift_report.merge(
        importance_report,
        on="feature",
        how="left",
    )


    report[
        "model_importance"
    ] = report[
        "model_importance"
    ].fillna(
        0
    )


    # -----------------------------------------------------
    # ROOT CAUSE SCORE
    #
    # Drift Score × Model Importance
    # -----------------------------------------------------

    report[
        "root_cause_score"
    ] = (
        report[
            "score"
        ]
        *
        report[
            "model_importance"
        ]
    )


    # -----------------------------------------------------
    # Convert to easier-to-read percentage style score
    # -----------------------------------------------------

    report[
        "root_cause_score"
    ] = (
        report[
            "root_cause_score"
        ]
        *
        100
    )


    # -----------------------------------------------------
    # ASSIGN PRIORITY
    # -----------------------------------------------------

    def assign_priority(row):

        if (
            row[
                "drift_level"
            ]
            ==
            "HIGH"
            and
            row[
                "model_importance"
            ]
            >=
            0.10
        ):

            return "HIGH"


        elif (
            row[
                "drift_level"
            ]
            in [
                "HIGH",
                "MODERATE",
            ]
            and
            row[
                "model_importance"
            ]
            >=
            0.05
        ):

            return "MEDIUM"


        return "LOW"


    report[
        "root_cause_priority"
    ] = report.apply(
        assign_priority,
        axis=1,
    )


    report = report.sort_values(
        by=
            "root_cause_score",

        ascending=
            False,
    )


    return report


# ---------------------------------------------------------
# 5. GENERATE RECOMMENDATION
# ---------------------------------------------------------

def generate_recommendation(
    root_cause_report,
):

    high_priority = root_cause_report[
        root_cause_report[
            "root_cause_priority"
        ]
        ==
        "HIGH"
    ]


    if not high_priority.empty:

        top_features = high_priority[
            "feature"
        ].head(
            3
        ).tolist()


        feature_text = ", ".join(
            top_features
        )


        return (
            "Investigate recent changes in "
            f"{feature_text}. "
            "These features show significant drift "
            "and are important to the current model. "
            "Consider validating the production data "
            "and retraining the model using recent data."
        )


    medium_priority = root_cause_report[
        root_cause_report[
            "root_cause_priority"
        ]
        ==
        "MEDIUM"
    ]


    if not medium_priority.empty:

        return (
            "Moderate model risk detected. "
            "Continue monitoring the changed features "
            "before triggering automatic retraining."
        )


    return (
        "No major root cause detected. "
        "Current feature changes appear unlikely "
        "to significantly affect the model."
    )


# ---------------------------------------------------------
# 6. MAIN PROGRAM
# ---------------------------------------------------------

def main():

    print(
        "\nLoading trained model..."
    )


    pipeline = joblib.load(
        MODEL_FILE
    )


    print(
        "Pipeline steps:"
    )

    print(
        list(
            pipeline.named_steps.keys()
        )
    )


    print(
        "\nLoading datasets..."
    )


    reference_data = pd.read_csv(
        REFERENCE_DATA_FILE
    )


    production_data = pd.read_csv(
        PRODUCTION_DATA_FILE
    )


    # -----------------------------------------------------
    # DRIFT
    # -----------------------------------------------------

    drift_report = generate_drift_report(
        reference_data,
        production_data,
    )


    # -----------------------------------------------------
    # FEATURE IMPORTANCE
    # -----------------------------------------------------

    importance_report = (
        get_feature_importance(
            pipeline
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


    recommendation = (
        generate_recommendation(
            root_cause_report
        )
    )


    # -----------------------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------------------

    print("\n")

    print("=" * 90)


    print(
        "ROOT CAUSE ANALYSIS"
    )


    print("=" * 90)


    columns_to_show = [
        "feature",
        "drift_level",
        "score",
        "model_importance",
        "root_cause_score",
        "root_cause_priority",
    ]


    print(
        root_cause_report[
            columns_to_show
        ].to_string(
            index=False
        )
    )


    print("\n")

    print("=" * 90)


    print(
        "RECOMMENDATION"
    )


    print("=" * 90)


    print(
        recommendation
    )


    print("=" * 90)


if __name__ == "__main__":
    main()