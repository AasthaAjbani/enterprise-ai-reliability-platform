from pathlib import Path
import inspect
import json

import joblib
import mlflow
import mlflow.sklearn

from mlflow.tracking import MlflowClient


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MLFLOW_DB_PATH = (
    PROJECT_ROOT
    / "mlflow.db"
).resolve()

MLFLOW_TRACKING_URI = (
    f"sqlite:///{MLFLOW_DB_PATH.as_posix()}"
)

EXPERIMENT_NAME = (
    "Enterprise AI Reliability - Self Healing"
)

REGISTERED_MODEL_NAME = (
    "FraudDetectionModel"
)


# =========================================================
# ARTIFACT PATHS
# =========================================================

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
# VALIDATE REQUIRED FILES
# =========================================================

def validate_files():

    if not CHALLENGER_MODEL_PATH.exists():

        raise FileNotFoundError(
            "\nChallenger model not found:\n"
            f"{CHALLENGER_MODEL_PATH}\n\n"
            "Run this first:\n"
            "python -m scripts.train_challenger_model"
        )


    if not COMPARISON_REPORT_PATH.exists():

        raise FileNotFoundError(
            "\nComparison report not found:\n"
            f"{COMPARISON_REPORT_PATH}\n\n"
            "Run this first:\n"
            "python -m scripts.train_challenger_model"
        )


# =========================================================
# LOAD COMPARISON REPORT
# =========================================================

def load_comparison_report():

    with open(
        COMPARISON_REPORT_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# FIND CURRENT CHAMPION
# =========================================================

def find_current_champion(
    client: MlflowClient,
):

    # -----------------------------------------------------
    # First try the explicit "champion" alias.
    # -----------------------------------------------------

    try:

        champion = (
            client.get_model_version_by_alias(
                REGISTERED_MODEL_NAME,
                "champion",
            )
        )

        return champion

    except Exception:
        pass


    # -----------------------------------------------------
    # If champion alias does not exist yet,
    # find the newest version already in the registry.
    #
    # On the first run this should normally be Version 1,
    # which represents our original deployed model.
    # -----------------------------------------------------

    try:

        versions = list(
            client.search_model_versions(
                (
                    "name="
                    f"'{REGISTERED_MODEL_NAME}'"
                )
            )
        )

    except Exception:

        return None


    if not versions:

        return None


    versions.sort(
        key=lambda version:
            int(version.version),
        reverse=True,
    )


    return versions[0]


# =========================================================
# LOG + REGISTER CHALLENGER MODEL
# =========================================================

def log_challenger_model(
    challenger_model,
):

    # -----------------------------------------------------
    # MLflow / skops security
    # -----------------------------------------------------
    #
    # RandomForest models contain sklearn's internal:
    #
    #     sklearn.tree._tree.Tree
    #
    # Modern MLflow versions using skops refuse to serialize
    # this type unless we explicitly trust it.
    #
    # This model was trained locally by our own pipeline,
    # so we trust ONLY this required sklearn type.
    # -----------------------------------------------------

    trusted_types = [
        "sklearn.tree._tree.Tree"
    ]


    # -----------------------------------------------------
    # MLflow changed its sklearn log_model API.
    #
    # Some versions use:
    #
    #     name=
    #
    # while older versions use:
    #
    #     artifact_path=
    #
    # We detect the installed version automatically.
    # -----------------------------------------------------

    signature = inspect.signature(
        mlflow.sklearn.log_model
    )


    common_arguments = {

        "sk_model":
            challenger_model,

        "registered_model_name":
            REGISTERED_MODEL_NAME,

        "skops_trusted_types":
            trusted_types,
    }


    if "name" in signature.parameters:

        return mlflow.sklearn.log_model(
            name="challenger_model",
            **common_arguments,
        )


    return mlflow.sklearn.log_model(
        artifact_path="challenger_model",
        **common_arguments,
    )


# =========================================================
# FIND MODEL VERSION CREATED BY CURRENT RUN
# =========================================================

def find_version_for_run(
    client: MlflowClient,
    run_id: str,
):

    versions = list(
        client.search_model_versions(
            (
                "name="
                f"'{REGISTERED_MODEL_NAME}'"
            )
        )
    )


    matching_versions = [
        version
        for version in versions
        if version.run_id == run_id
    ]


    if not matching_versions:

        raise RuntimeError(
            "\nMLflow run completed, but the registered "
            "challenger model version could not be found."
        )


    matching_versions.sort(
        key=lambda version:
            int(version.version),
        reverse=True,
    )


    return matching_versions[0]


# =========================================================
# SET MODEL VERSION TAG
# =========================================================

def set_version_tag(
    client: MlflowClient,
    version,
    key: str,
    value: str,
):

    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=str(version),
        key=key,
        value=str(value),
    )


# =========================================================
# PRINT METRICS
# =========================================================

def print_comparison_summary(
    current_metrics,
    challenger_metrics,
    promotion,
):

    print(
        "\nCURRENT MODEL"
    )

    print(
        "-------------"
    )

    print(
        f"Accuracy : "
        f"{current_metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{current_metrics['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{current_metrics['recall']:.4f}"
    )

    print(
        f"F1       : "
        f"{current_metrics['f1']:.4f}"
    )


    print(
        "\nCHALLENGER MODEL"
    )

    print(
        "----------------"
    )

    print(
        f"Accuracy : "
        f"{challenger_metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{challenger_metrics['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{challenger_metrics['recall']:.4f}"
    )

    print(
        f"F1       : "
        f"{challenger_metrics['f1']:.4f}"
    )


    print(
        "\nIMPROVEMENT"
    )

    print(
        "-----------"
    )

    print(
        f"F1 improvement      : "
        f"{promotion['f1_improvement']:.4f}"
    )

    print(
        f"Recall improvement  : "
        f"{promotion['recall_improvement']:.4f}"
    )

    print(
        f"Precision change    : "
        f"{promotion['precision_change']:.4f}"
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
        " MLFLOW CHALLENGER REGISTRATION"
    )

    print(
        "=============================================="
    )


    # =====================================================
    # STEP 1
    # Validate required files
    # =====================================================

    print(
        "\nChecking challenger artifacts..."
    )

    validate_files()

    print(
        "Artifacts found."
    )


    # =====================================================
    # STEP 2
    # Configure MLflow
    # =====================================================

    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )


    print(
        "\nMLflow tracking URI:"
    )

    print(
        MLFLOW_TRACKING_URI
    )


    mlflow.set_experiment(
        EXPERIMENT_NAME
    )


    client = MlflowClient(
        tracking_uri=
            MLFLOW_TRACKING_URI
    )


    # =====================================================
    # STEP 3
    # Find current champion BEFORE registering challenger
    # =====================================================

    current_champion = (
        find_current_champion(
            client
        )
    )


    if current_champion:

        print(
            "\nCurrent registered model version:"
        )

        print(
            current_champion.version
        )


        print(
            "\nCurrent model will remain champion "
            "during challenger registration."
        )

    else:

        print(
            "\nNo existing registered model version "
            "was found."
        )


    # =====================================================
    # STEP 4
    # Load comparison report
    # =====================================================

    print(
        "\nLoading challenger comparison report..."
    )


    comparison = (
        load_comparison_report()
    )


    current_metrics = (
        comparison[
            "current_model"
        ]
    )


    challenger_metrics = (
        comparison[
            "challenger_model"
        ]
    )


    promotion = (
        comparison[
            "promotion_analysis"
        ]
    )


    print_comparison_summary(
        current_metrics,
        challenger_metrics,
        promotion,
    )


    # =====================================================
    # STEP 5
    # Load challenger model
    # =====================================================

    print(
        "\nLoading challenger model..."
    )


    challenger_model = (
        joblib.load(
            CHALLENGER_MODEL_PATH
        )
    )


    print(
        "Challenger model loaded."
    )


    # =====================================================
    # STEP 6
    # Start MLflow run
    # =====================================================

    with mlflow.start_run(
        run_name=
            "challenger_model_evaluation"
    ) as run:

        run_id = (
            run.info.run_id
        )


        print(
            "\nMLflow run ID:"
        )

        print(
            run_id
        )


        # =================================================
        # TAGS
        # =================================================

        mlflow.set_tags(
            {
                "system":
                    "enterprise-ai-reliability",

                "pipeline_stage":
                    "challenger_evaluation",

                "model_role":
                    "challenger",

                "promotion_decision":
                    comparison[
                        "decision"
                    ],

                "validation_dataset":
                    "held-out-production",

                "deployment_status":
                    "not-promoted",
            }
        )


        # =================================================
        # PARAMETERS
        # =================================================

        validation_strategy = (
            comparison[
                "validation_strategy"
            ]
        )


        criteria = (
            promotion[
                "criteria"
            ]
        )


        mlflow.log_params(
            {
                "validation_fraction":
                    validation_strategy[
                        "production_validation_fraction"
                    ],

                "random_state":
                    validation_strategy[
                        "random_state"
                    ],

                "minimum_f1_improvement":
                    criteria[
                        "minimum_f1_improvement"
                    ],

                "minimum_recall_improvement":
                    criteria[
                        "minimum_recall_improvement"
                    ],

                "maximum_precision_drop":
                    criteria[
                        "maximum_precision_drop"
                    ],
            }
        )


        # =================================================
        # CURRENT MODEL METRICS
        # =================================================

        mlflow.log_metrics(
            {
                "current_accuracy":
                    current_metrics[
                        "accuracy"
                    ],

                "current_precision":
                    current_metrics[
                        "precision"
                    ],

                "current_recall":
                    current_metrics[
                        "recall"
                    ],

                "current_f1":
                    current_metrics[
                        "f1"
                    ],
            }
        )


        # =================================================
        # CHALLENGER MODEL METRICS
        # =================================================

        mlflow.log_metrics(
            {
                "challenger_accuracy":
                    challenger_metrics[
                        "accuracy"
                    ],

                "challenger_precision":
                    challenger_metrics[
                        "precision"
                    ],

                "challenger_recall":
                    challenger_metrics[
                        "recall"
                    ],

                "challenger_f1":
                    challenger_metrics[
                        "f1"
                    ],
            }
        )


        # =================================================
        # IMPROVEMENT METRICS
        # =================================================

        mlflow.log_metrics(
            {
                "f1_improvement":
                    promotion[
                        "f1_improvement"
                    ],

                "recall_improvement":
                    promotion[
                        "recall_improvement"
                    ],

                "precision_change":
                    promotion[
                        "precision_change"
                    ],

                "promotion_eligible":
                    (
                        1.0
                        if promotion[
                            "promotion_eligible"
                        ]
                        else 0.0
                    ),
            }
        )


        # =================================================
        # LOG COMPARISON REPORT
        # =================================================

        mlflow.log_dict(
            comparison,
            "reports/challenger_comparison.json",
        )


        # =================================================
        # LOG ORIGINAL JOBLIB ARTIFACT
        # =================================================

        mlflow.log_artifact(
            str(
                CHALLENGER_MODEL_PATH
            ),
            artifact_path=
                "artifacts",
        )


        # =================================================
        # REGISTER CHALLENGER
        # =================================================

        print(
            "\nRegistering challenger model..."
        )


        log_challenger_model(
            challenger_model
        )


        print(
            "Model logging completed."
        )


    # =====================================================
    # STEP 7
    # Find newly registered model version
    # =====================================================

    challenger_version = (
        find_version_for_run(
            client,
            run_id,
        )
    )


    print(
        "\nChallenger registered as version:"
    )

    print(
        challenger_version.version
    )


    # =====================================================
    # STEP 8
    # Add challenger version tags
    # =====================================================

    set_version_tag(
        client,
        challenger_version.version,
        "model_role",
        "challenger",
    )


    set_version_tag(
        client,
        challenger_version.version,
        "promotion_decision",
        comparison[
            "decision"
        ],
    )


    set_version_tag(
        client,
        challenger_version.version,
        "deployment_status",
        "not-promoted",
    )


    set_version_tag(
        client,
        challenger_version.version,
        "validation_dataset",
        "held-out-production",
    )


    # =====================================================
    # STEP 9
    # Assign challenger alias
    # =====================================================

    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME,
        "challenger",
        challenger_version.version,
    )


    print(
        "\nAlias assigned:"
    )

    print(
        "challenger -> version "
        f"{challenger_version.version}"
    )


    # =====================================================
    # STEP 10
    # Preserve current champion
    # =====================================================

    if current_champion:

        client.set_registered_model_alias(
            REGISTERED_MODEL_NAME,
            "champion",
            current_champion.version,
        )


        set_version_tag(
            client,
            current_champion.version,
            "model_role",
            "champion",
        )


        set_version_tag(
            client,
            current_champion.version,
            "deployment_status",
            "active",
        )


        print(
            "\nAlias retained:"
        )

        print(
            "champion -> version "
            f"{current_champion.version}"
        )


    # =====================================================
    # STEP 11
    # FINAL RESULT
    # =====================================================

    print(
        "\n=============================================="
    )

    print(
        " MLFLOW REGISTRATION COMPLETE"
    )

    print(
        "=============================================="
    )


    print(
        "\nRegistered model:"
    )

    print(
        REGISTERED_MODEL_NAME
    )


    print(
        "\nChallenger version:"
    )

    print(
        challenger_version.version
    )


    if current_champion:

        print(
            "\nChampion version:"
        )

        print(
            current_champion.version
        )


    print(
        "\nPromotion decision:"
    )

    print(
        comparison[
            "decision"
        ]
    )


    print(
        "\nPromotion eligible:"
    )

    print(
        promotion[
            "promotion_eligible"
        ]
    )


    print(
        "\nIMPORTANT:"
    )

    print(
        "The challenger has been registered "
        "in MLflow, but it has NOT replaced "
        "the champion model."
    )


# =========================================================
# RUN SCRIPT
# =========================================================

if __name__ == "__main__":
    main()