from pathlib import Path
from datetime import datetime, timezone
import json
import os
import shutil

import mlflow

from mlflow.tracking import MlflowClient


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

CURRENT_MODEL_PATH = (
    MODELS_DIR
    / "fraud_model.joblib"
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
# LOAD DEPLOYMENT STATE
# =========================================================

def load_deployment_state():

    if not DEPLOYMENT_STATE_PATH.exists():

        raise FileNotFoundError(
            "\nNo deployment state exists.\n"
            "A model must be promoted before "
            "rollback is available."
        )


    with open(
        DEPLOYMENT_STATE_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# =========================================================
# RESTORE MODEL FILE
# =========================================================

def restore_model(
    backup_path: Path,
):

    if not backup_path.exists():

        raise FileNotFoundError(
            "\nRollback model backup "
            "could not be found:\n"
            f"{backup_path}"
        )


    temporary_path = (
        MODELS_DIR
        / "fraud_model.rollback.joblib"
    )


    shutil.copy2(
        backup_path,
        temporary_path,
    )


    os.replace(
        temporary_path,
        CURRENT_MODEL_PATH,
    )


# =========================================================
# SET TAG
# =========================================================

def set_version_tag(
    client,
    version,
    key,
    value,
):

    client.set_model_version_tag(
        name=
            REGISTERED_MODEL_NAME,

        version=
            str(version),

        key=
            str(key),

        value=
            str(value),
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
        " MODEL ROLLBACK"
    )

    print(
        "=============================================="
    )


    # =====================================================
    # Read deployment history
    # =====================================================

    state = (
        load_deployment_state()
    )


    if not state.get(
        "rollback_available",
        False,
    ):

        print(
            "\nRollback is not currently available."
        )

        return


    current_version = (
        state[
            "champion_version"
        ]
    )


    previous_version = (
        state[
            "previous_champion_version"
        ]
    )


    backup_path = Path(
        state[
            "previous_model_backup"
        ]
    )


    print(
        "\nCurrent champion:"
    )

    print(
        f"Version {current_version}"
    )


    print(
        "\nRollback target:"
    )

    print(
        f"Version {previous_version}"
    )


    print(
        "\nRestoring model artifact..."
    )


    # =====================================================
    # Restore previous model
    # =====================================================

    restore_model(
        backup_path
    )


    print(
        "Previous model artifact restored."
    )


    # =====================================================
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
    # Restore MLflow champion alias
    # =====================================================

    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME,
        "champion",
        previous_version,
    )


    client.set_registered_model_alias(
        REGISTERED_MODEL_NAME,
        "challenger",
        current_version,
    )


    set_version_tag(
        client,
        previous_version,
        "model_role",
        "champion",
    )


    set_version_tag(
        client,
        previous_version,
        "deployment_status",
        "active-after-rollback",
    )


    set_version_tag(
        client,
        current_version,
        "model_role",
        "rolled_back",
    )


    set_version_tag(
        client,
        current_version,
        "deployment_status",
        "inactive",
    )


    # =====================================================
    # Update deployment state
    # =====================================================

    state[
        "champion_version"
    ] = previous_version


    state[
        "rolled_back_version"
    ] = current_version


    state[
        "rolled_back_at"
    ] = datetime.now(
        timezone.utc
    ).isoformat()


    state[
        "rollback_available"
    ] = False


    state[
        "deployment_status"
    ] = "ROLLED_BACK"


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


    # =====================================================
    # DONE
    # =====================================================

    print(
        "\n=============================================="
    )

    print(
        " ROLLBACK SUCCESSFUL"
    )

    print(
        "=============================================="
    )


    print(
        "\nChampion restored:"
    )

    print(
        f"Version {previous_version}"
    )


    print(
        "\nRolled-back model:"
    )

    print(
        f"Version {current_version}"
    )


    print(
        "\nProduction model:"
    )

    print(
        CURRENT_MODEL_PATH
    )


# =========================================================
# EXECUTE
# =========================================================

if __name__ == "__main__":
    main()