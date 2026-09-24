from pathlib import Path
from datetime import datetime, timezone
import json
import os
import shutil

import mlflow

from mlflow.tracking import MlflowClient


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

ARCHIVE_DIR = (
    MODELS_DIR
    / "archive"
)

CURRENT_MODEL_PATH = (
    MODELS_DIR
    / "fraud_model.joblib"
)

CHALLENGER_MODEL_PATH = (
    MODELS_DIR
    / "challenger_fraud_model.joblib"
)

COMPARISON_REPORT_PATH = (
    MODELS_DIR
    / "challenger_comparison.json"
)

DEPLOYMENT_STATE_PATH = (
    MODELS_DIR
    / "deployment_state.json"
)


MLFLOW_DB_PATH = (
    PROJECT_ROOT
    / "mlflow.db"
).resolve()

MLFLOW_TRACKING_URI = (
    f"sqlite:///{MLFLOW_DB_PATH.as_posix()}"
)

REGISTERED_MODEL_NAME = (
    "FraudDetectionModel"
)


# =========================================================
# FILE VALIDATION
# =========================================================

def validate_files():

    required_files = [
        CURRENT_MODEL_PATH,
        CHALLENGER_MODEL_PATH,
        COMPARISON_REPORT_PATH,
    ]


    missing_files = [
        path
        for path in required_files
        if not path.exists()
    ]


    if missing_files:

        formatted = "\n".join(
            str(path)
            for path in missing_files
        )

        raise FileNotFoundError(
            "\nRequired files are missing:\n"
            f"{formatted}"
        )


# =========================================================
# LOAD COMPARISON
# =========================================================

def load_comparison():

    with open(
        COMPARISON_REPORT_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# LOAD PREVIOUS DEPLOYMENT STATE
# =========================================================

def load_deployment_state():

    if not DEPLOYMENT_STATE_PATH.exists():
        return None


    with open(
        DEPLOYMENT_STATE_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# GET MODEL ALIAS
# =========================================================

def get_alias(
    client: MlflowClient,
    alias: str,
):

    try:

        return (
            client
            .get_model_version_by_alias(
                REGISTERED_MODEL_NAME,
                alias,
            )
        )

    except Exception:

        return None


# =========================================================
# CREATE BACKUP
# =========================================================

def backup_current_model(
    champion_version: str,
):

    ARCHIVE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    backup_path = (
        ARCHIVE_DIR
        / (
            f"fraud_model_v"
            f"{champion_version}.joblib"
        )
    )


    if backup_path.exists():

        print(
            "\nBackup already exists:"
        )

        print(
            backup_path
        )

        return backup_path


    shutil.copy2(
        CURRENT_MODEL_PATH,
        backup_path,
    )


    print(
        "\nCurrent production model backed up:"
    )

    print(
        backup_path
    )


    return backup_path


# =========================================================
# ATOMICALLY REPLACE ACTIVE MODEL
# =========================================================

def activate_challenger_model():

    temporary_path = (
        MODELS_DIR
        / "fraud_model.promoting.joblib"
    )


    # -----------------------------------------------------
    # Copy challenger into a temporary file first.
    #
    # We do not write directly over the production file.
    # -----------------------------------------------------

    shutil.copy2(
        CHALLENGER_MODEL_PATH,
        temporary_path,
    )


    # -----------------------------------------------------
    # os.replace is atomic on the same filesystem.
    # -----------------------------------------------------

    os.replace(
        temporary_path,
        CURRENT_MODEL_PATH,
    )


    print(
        "\nActive model file replaced successfully."
    )

    print(
        CURRENT_MODEL_PATH
    )


# =========================================================
# UPDATE MODEL VERSION TAG
# =========================================================

def set_version_tag(
    client: MlflowClient,
    version,
    key: str,
    value: str,
):

    client.set_model_version_tag(
        name=
            REGISTERED_MODEL_NAME,

        version=
            str(version),

        key=
            key,

        value=
            str(value),
    )


# =========================================================
# SAVE DEPLOYMENT STATE
# =========================================================

def save_deployment_state(
    old_champion_version,
    new_champion_version,
    backup_path,
    comparison,
):

    previous_state = (
        load_deployment_state()
    )


    state = {

        "registered_model":
            REGISTERED_MODEL_NAME,

        "champion_version":
            str(
                new_champion_version
            ),

        "previous_champion_version":
            str(
                old_champion_version
            ),

        "active_model_path":
            str(
                CURRENT_MODEL_PATH
            ),

        "previous_model_backup":
            str(
                backup_path
            ),

        "challenger_source_path":
            str(
                CHALLENGER_MODEL_PATH
            ),

        "promotion_decision":
            comparison[
                "decision"
            ],

        "promoted_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "rollback_available":
            True,

        "previous_deployment_state":
            previous_state,
    }


    with open(
        DEPLOYMENT_STATE_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            state,
            file,
            indent=4,
        )


    print(
        "\nDeployment state saved:"
    )

    print(
        DEPLOYMENT_STATE_PATH
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
        " CONTROLLED MODEL PROMOTION"
    )

    print(
        "=============================================="
    )


    # =====================================================
    # STEP 1
    # Validate local artifacts
    # =====================================================

    print(
        "\nChecking deployment artifacts..."
    )


    validate_files()


    print(
        "Required artifacts found."
    )


    # =====================================================
    # STEP 2
    # Read quality-gate decision
    # =====================================================

    comparison = (
        load_comparison()
    )


    promotion = (
        comparison[
            "promotion_analysis"
        ]
    )


    decision = (
        comparison[
            "decision"
        ]
    )


    print(
        "\nQuality-gate decision:"
    )

    print(
        decision
    )


    print(
        "\nPromotion eligible:"
    )

    print(
        promotion[
            "promotion_eligible"
        ]
    )


    # =====================================================
    # STEP 3
    # STOP if gate failed
    # =====================================================

    if not promotion[
        "promotion_eligible"
    ]:

        print(
            "\n=============================================="
        )

        print(
            " PROMOTION BLOCKED"
        )

        print(
            "=============================================="
        )


        print(
            "\nThe challenger failed "
            "the promotion quality gate."
        )


        print(
            "\nProduction model remains unchanged."
        )

        return


    # =====================================================
    # STEP 4
    # Configure MLflow
    # =====================================================

    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )


    client = MlflowClient(
        tracking_uri=
            MLFLOW_TRACKING_URI
    )


    # =====================================================
    # STEP 5
    # Get current aliases
    # =====================================================

    champion = (
        get_alias(
            client,
            "champion",
        )
    )


    challenger = (
        get_alias(
            client,
            "challenger",
        )
    )


    if champion is None:

        raise RuntimeError(
            "\nNo MLflow champion alias found."
        )


    if challenger is None:

        raise RuntimeError(
            "\nNo MLflow challenger alias found."
        )


    champion_version = (
        str(
            champion.version
        )
    )


    challenger_version = (
        str(
            challenger.version
        )
    )


    print(
        "\nCurrent champion:"
    )

    print(
        f"Version {champion_version}"
    )


    print(
        "\nCandidate challenger:"
    )

    print(
        f"Version {challenger_version}"
    )


    # =====================================================
    # STEP 6
    # Prevent duplicate promotion
    # =====================================================

    if (
        champion_version
        ==
        challenger_version
    ):

        print(
            "\nChallenger is already champion."
        )

        print(
            "No deployment changes required."
        )

        return


    # =====================================================
    # STEP 7
    # Backup current production model
    # =====================================================

    backup_path = (
        backup_current_model(
            champion_version
        )
    )


    # =====================================================
    # STEP 8
    # Activate challenger locally
    # =====================================================

    print(
        "\nActivating challenger model..."
    )


    activate_challenger_model()


    # =====================================================
    # STEP 9
    # Update MLflow aliases
    # =====================================================

    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME,
        "previous_champion",
        champion_version,
    )


    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME,
        "champion",
        challenger_version,
    )


    # Keep challenger alias pointing at the model that
    # originally entered this promotion process.
    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME,
        "challenger",
        challenger_version,
    )


    # =====================================================
    # STEP 10
    # Update previous champion metadata
    # =====================================================

    set_version_tag(
        client,
        champion_version,
        "model_role",
        "previous_champion",
    )


    set_version_tag(
        client,
        champion_version,
        "deployment_status",
        "rollback-ready",
    )


    # =====================================================
    # STEP 11
    # Update new champion metadata
    # =====================================================

    set_version_tag(
        client,
        challenger_version,
        "model_role",
        "champion",
    )


    set_version_tag(
        client,
        challenger_version,
        "deployment_status",
        "active",
    )


    set_version_tag(
        client,
        challenger_version,
        "promoted_at",
        datetime.now(
            timezone.utc
        ).isoformat(),
    )


    # =====================================================
    # STEP 12
    # Save deployment state
    # =====================================================

    save_deployment_state(
        old_champion_version=
            champion_version,

        new_champion_version=
            challenger_version,

        backup_path=
            backup_path,

        comparison=
            comparison,
    )


    # =====================================================
    # FINISHED
    # =====================================================

    print(
        "\n=============================================="
    )

    print(
        " PROMOTION SUCCESSFUL"
    )

    print(
        "=============================================="
    )


    print(
        "\nPrevious champion:"
    )

    print(
        f"Version {champion_version}"
    )


    print(
        "\nNew champion:"
    )

    print(
        f"Version {challenger_version}"
    )


    print(
        "\nMLflow aliases:"
    )

    print(
        "champion -> "
        f"version {challenger_version}"
    )

    print(
        "previous_champion -> "
        f"version {champion_version}"
    )


    print(
        "\nProduction artifact:"
    )

    print(
        CURRENT_MODEL_PATH
    )


    print(
        "\nRollback backup:"
    )

    print(
        backup_path
    )


    print(
        "\nRollback is available."
    )


# =========================================================
# EXECUTE
# =========================================================

if __name__ == "__main__":
    main()