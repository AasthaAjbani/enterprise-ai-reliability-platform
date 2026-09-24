from pathlib import Path
import json


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SELF_HEALING_STATE_PATH = (
    PROJECT_ROOT
    / "models"
    / "self_healing_state.json"
)


# =========================================================
# LOAD SELF-HEALING STATE
# =========================================================

def get_self_healing_status():

    if not SELF_HEALING_STATE_PATH.exists():

        return {
            "status":
                "NOT_RUN",

            "current_stage":
                None,

            "healing_required":
                None,

            "healing_trigger":
                None,

            "quality_gate":
                None,

            "promotion_attempted":
                False,

            "promotion_completed":
                False,

            "verification_completed":
                False,

            "champion_version":
                None,

            "previous_champion_version":
                None,

            "rollback_available":
                False,

            "started_at":
                None,

            "completed_at":
                None,

            "duration_seconds":
                None,

            "error":
                None,
        }


    with open(
        SELF_HEALING_STATE_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        state = json.load(file)


    return state