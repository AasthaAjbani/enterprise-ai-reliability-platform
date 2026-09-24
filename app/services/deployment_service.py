from pathlib import Path
import json


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

DEPLOYMENT_STATE_PATH = (
    MODELS_DIR
    / "deployment_state.json"
)

COMPARISON_REPORT_PATH = (
    MODELS_DIR
    / "challenger_comparison.json"
)


# =========================================================
# JSON LOADER
# =========================================================

def load_json_file(
    path: Path,
):

    if not path.exists():
        return None


    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# DEPLOYMENT STATUS
# =========================================================

def get_deployment_status():

    deployment_state = (
        load_json_file(
            DEPLOYMENT_STATE_PATH
        )
    )


    comparison = (
        load_json_file(
            COMPARISON_REPORT_PATH
        )
    )


    # -----------------------------------------------------
    # No deployment has happened yet
    # -----------------------------------------------------

    if deployment_state is None:

        return {
            "status":
                "NOT_DEPLOYED",

            "registered_model":
                "FraudDetectionModel",

            "champion_version":
                None,

            "previous_champion_version":
                None,

            "rollback_available":
                False,

            "promoted_at":
                None,

            "quality_gate":
                None,

            "validation":
                None,
        }


    # -----------------------------------------------------
    # Determine deployment state
    # -----------------------------------------------------

    deployment_status = (
        deployment_state.get(
            "deployment_status"
        )
    )


    if deployment_status == "ROLLED_BACK":

        status = "ROLLED_BACK"

    else:

        status = "PROMOTED"


    # -----------------------------------------------------
    # Quality gate
    # -----------------------------------------------------

    quality_gate = None

    validation = None


    if comparison:

        promotion = (
            comparison.get(
                "promotion_analysis",
                {}
            )
        )


        quality_gate = {

            "decision":
                comparison.get(
                    "decision"
                ),

            "eligible":
                promotion.get(
                    "promotion_eligible"
                ),

            "f1_improvement":
                promotion.get(
                    "f1_improvement"
                ),

            "recall_improvement":
                promotion.get(
                    "recall_improvement"
                ),

            "precision_change":
                promotion.get(
                    "precision_change"
                ),

            "criteria":
                promotion.get(
                    "criteria"
                ),
        }


        validation = {

            "strategy":
                comparison
                .get(
                    "validation_strategy",
                    {}
                )
                .get(
                    "comparison_note"
                ),

            "validation_fraction":
                comparison
                .get(
                    "validation_strategy",
                    {}
                )
                .get(
                    "production_validation_fraction"
                ),

            "previous_model":
                comparison.get(
                    "current_model"
                ),

            "promoted_model":
                comparison.get(
                    "challenger_model"
                ),
        }


    # -----------------------------------------------------
    # API RESPONSE
    # -----------------------------------------------------

    return {

        "status":
            status,

        "registered_model":
            deployment_state.get(
                "registered_model",
                "FraudDetectionModel",
            ),

        "champion_version":
            deployment_state.get(
                "champion_version"
            ),

        "previous_champion_version":
            deployment_state.get(
                "previous_champion_version"
            ),

        "rollback_available":
            deployment_state.get(
                "rollback_available",
                False,
            ),

        "promoted_at":
            deployment_state.get(
                "promoted_at"
            ),

        "quality_gate":
            quality_gate,

        "validation":
            validation,
    }