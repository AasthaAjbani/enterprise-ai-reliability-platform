from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import sys
import time

from app.services.healing_trigger_service import (
    evaluate_healing_trigger,
)


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)

COMPARISON_REPORT_PATH = (
    MODELS_DIR
    / "challenger_comparison.json"
)

DEPLOYMENT_STATE_PATH = (
    MODELS_DIR
    / "deployment_state.json"
)

PIPELINE_STATE_PATH = (
    MODELS_DIR
    / "self_healing_state.json"
)


# =========================================================
# PIPELINE COMMANDS
# =========================================================

TRAIN_COMMAND = [
    sys.executable,
    "-m",
    "scripts.train_challenger_model",
]

REGISTER_COMMAND = [
    sys.executable,
    "-m",
    "scripts.register_challenger_mlflow",
]

PROMOTE_COMMAND = [
    sys.executable,
    "-m",
    "scripts.promote_challenger",
]

VERIFY_COMMAND = [
    sys.executable,
    "-m",
    "scripts.verify_promotion",
]


# =========================================================
# TIME
# =========================================================

def utc_now():

    return datetime.now(
        timezone.utc
    ).isoformat()


# =========================================================
# LOAD JSON
# =========================================================

def load_json(
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
# SAVE PIPELINE STATE
# =========================================================

def save_pipeline_state(
    state,
):

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    with open(
        PIPELINE_STATE_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            state,
            file,
            indent=4,
        )


# =========================================================
# UPDATE PIPELINE STATE
# =========================================================

def update_state(
    state,
    **changes,
):

    state.update(
        changes
    )


    state[
        "updated_at"
    ] = utc_now()


    save_pipeline_state(
        state
    )


# =========================================================
# RUN SUBPROCESS
# =========================================================

def run_command(
    title,
    command,
):

    print(
        "\n"
        "=============================================="
    )

    print(
        f" {title}"
    )

    print(
        "=============================================="
    )


    print(
        "\nRunning:"
    )

    print(
        " ".join(
            command
        )
    )

    print()


    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )


    if result.returncode != 0:

        raise RuntimeError(
            f"{title} failed with "
            f"exit code "
            f"{result.returncode}."
        )


    print(
        f"\n{title} completed successfully."
    )


# =========================================================
# PRINT HEALING TRIGGER
# =========================================================

def print_healing_trigger(
    trigger,
):

    print(
        "\n"
        "=============================================="
    )

    print(
        " STAGE 0 - HEALING TRIGGER"
    )

    print(
        "=============================================="
    )


    print(
        "\nSystem status:"
    )

    print(
        trigger[
            "status"
        ]
    )


    print(
        "\nHealing required:"
    )

    print(
        trigger[
            "healing_required"
        ]
    )


    print(
        "\nReason:"
    )

    print(
        trigger[
            "reason"
        ]
    )


    print(
        "\nBASELINE PERFORMANCE"
    )

    print(
        "--------------------"
    )


    baseline = (
        trigger[
            "baseline"
        ]
    )


    print(
        f"Accuracy : "
        f"{baseline['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{baseline['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{baseline['recall']:.4f}"
    )

    print(
        f"F1       : "
        f"{baseline['f1']:.4f}"
    )


    print(
        "\nACTIVE MODEL PERFORMANCE"
    )

    print(
        "------------------------"
    )


    production = (
        trigger[
            "production"
        ]
    )


    print(
        f"Accuracy : "
        f"{production['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{production['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{production['recall']:.4f}"
    )

    print(
        f"F1       : "
        f"{production['f1']:.4f}"
    )


    degradation = (
        trigger[
            "degradation"
        ]
    )


    print(
        "\nDEGRADATION"
    )

    print(
        "-----------"
    )


    print(
        f"F1 drop    : "
        f"{degradation['f1_drop']:+.4f}"
    )

    print(
        f"Recall drop: "
        f"{degradation['recall_drop']:+.4f}"
    )


# =========================================================
# QUALITY GATE
# =========================================================

def evaluate_quality_gate():

    comparison = (
        load_json(
            COMPARISON_REPORT_PATH
        )
    )


    if comparison is None:

        raise FileNotFoundError(
            "\nChallenger comparison "
            "report was not generated."
        )


    promotion = (
        comparison.get(
            "promotion_analysis",
            {}
        )
    )


    eligible = bool(
        promotion.get(
            "promotion_eligible",
            False,
        )
    )


    return (
        eligible,
        comparison,
    )


# =========================================================
# PRINT QUALITY GATE
# =========================================================

def print_quality_gate(
    comparison,
):

    promotion = (
        comparison[
            "promotion_analysis"
        ]
    )


    current = (
        comparison[
            "current_model"
        ]
    )


    challenger = (
        comparison[
            "challenger_model"
        ]
    )


    print(
        "\n"
        "=============================================="
    )

    print(
        " STAGE 2 - QUALITY GATE"
    )

    print(
        "=============================================="
    )


    print(
        "\nCURRENT MODEL"
    )

    print(
        "-------------"
    )


    print(
        f"Accuracy : "
        f"{current['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{current['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{current['recall']:.4f}"
    )

    print(
        f"F1       : "
        f"{current['f1']:.4f}"
    )


    print(
        "\nCHALLENGER MODEL"
    )

    print(
        "----------------"
    )


    print(
        f"Accuracy : "
        f"{challenger['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{challenger['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{challenger['recall']:.4f}"
    )

    print(
        f"F1       : "
        f"{challenger['f1']:.4f}"
    )


    print(
        "\nIMPROVEMENT"
    )

    print(
        "-----------"
    )


    print(
        f"F1 improvement     : "
        f"{promotion['f1_improvement']:+.4f}"
    )

    print(
        f"Recall improvement : "
        f"{promotion['recall_improvement']:+.4f}"
    )

    print(
        f"Precision change   : "
        f"{promotion['precision_change']:+.4f}"
    )


    print(
        "\nPromotion eligible:"
    )

    print(
        promotion[
            "promotion_eligible"
        ]
    )


# =========================================================
# MAIN
# =========================================================

def main():

    started_at = (
        utc_now()
    )


    start_time = (
        time.perf_counter()
    )


    # =====================================================
    # INITIAL PIPELINE STATE
    # =====================================================

    state = {

        "pipeline":
            "enterprise-ai-self-healing",

        "status":
            "RUNNING",

        "current_stage":
            "INITIALIZING",

        "started_at":
            started_at,

        "updated_at":
            started_at,

        "completed_at":
            None,

        "healing_trigger":
            None,

        "healing_required":
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

        "failure_stage":
            None,

        "error":
            None,
    }


    save_pipeline_state(
        state
    )


    print(
        "\n"
        "===================================================="
    )

    print(
        " ENTERPRISE AI RELIABILITY PLATFORM"
    )

    print(
        " CONDITIONAL SELF-HEALING PIPELINE"
    )

    print(
        "===================================================="
    )


    print(
        "\nPipeline started:"
    )

    print(
        started_at
    )


    try:

        # =================================================
        # STAGE 0
        # EVALUATE WHETHER HEALING IS REQUIRED
        # =================================================

        update_state(
            state,

            current_stage=
                "EVALUATING_HEALING_TRIGGER",
        )


        trigger = (
            evaluate_healing_trigger()
        )


        print_healing_trigger(
            trigger
        )


        state[
            "healing_trigger"
        ] = trigger


        state[
            "healing_required"
        ] = trigger[
            "healing_required"
        ]


        save_pipeline_state(
            state
        )


        # =================================================
        # STOP WHEN MODEL IS HEALTHY
        # =================================================

        if not trigger[
            "healing_required"
        ]:

            completed_at = (
                utc_now()
            )


            duration = (
                time.perf_counter()
                -
                start_time
            )


            deployment = (
                load_json(
                    DEPLOYMENT_STATE_PATH
                )
            )


            update_state(
                state,

                status=
                    "NO_HEALING_REQUIRED",

                current_stage=
                    "FINISHED",

                completed_at=
                    completed_at,

                duration_seconds=
                    round(
                        duration,
                        2,
                    ),

                champion_version=
                    (
                        deployment.get(
                            "champion_version"
                        )
                        if deployment
                        else None
                    ),

                previous_champion_version=
                    (
                        deployment.get(
                            "previous_champion_version"
                        )
                        if deployment
                        else None
                    ),

                rollback_available=
                    (
                        deployment.get(
                            "rollback_available"
                        )
                        if deployment
                        else False
                    ),
            )


            print(
                "\n"
                "===================================================="
            )

            print(
                " SELF-HEALING CHECK COMPLETE"
            )

            print(
                "===================================================="
            )


            print(
                "\nResult:"
            )

            print(
                "NO_HEALING_REQUIRED"
            )


            print(
                "\nThe active model is healthy."
            )


            print(
                "\nNo challenger was trained."
            )


            print(
                "No MLflow model version was created."
            )


            print(
                "No production model was changed."
            )


            print(
                "\nDuration:"
            )

            print(
                f"{duration:.2f} seconds"
            )


            return


        # =================================================
        # STAGE 1
        # TRAIN CHALLENGER
        # =================================================

        update_state(
            state,

            current_stage=
                "TRAINING_CHALLENGER",
        )


        run_command(
            "STAGE 1 - TRAIN CHALLENGER",
            TRAIN_COMMAND,
        )


        # =================================================
        # STAGE 2
        # QUALITY GATE
        # =================================================

        update_state(
            state,

            current_stage=
                "QUALITY_GATE",
        )


        (
            eligible,
            comparison,
        ) = evaluate_quality_gate()


        print_quality_gate(
            comparison
        )


        promotion = (
            comparison[
                "promotion_analysis"
            ]
        )


        state[
            "quality_gate"
        ] = {

            "eligible":
                eligible,

            "decision":
                comparison.get(
                    "decision"
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
        }


        save_pipeline_state(
            state
        )


        # =================================================
        # STOP WHEN CHALLENGER FAILS
        # =================================================

        if not eligible:

            completed_at = (
                utc_now()
            )


            duration = (
                time.perf_counter()
                -
                start_time
            )


            update_state(
                state,

                status=
                    "COMPLETED_NO_PROMOTION",

                current_stage=
                    "FINISHED",

                completed_at=
                    completed_at,

                duration_seconds=
                    round(
                        duration,
                        2,
                    ),
            )


            print(
                "\n"
                "===================================================="
            )

            print(
                " SELF-HEALING PIPELINE COMPLETE"
            )

            print(
                "===================================================="
            )


            print(
                "\nResult:"
            )

            print(
                "CHALLENGER_REJECTED"
            )


            print(
                "\nThe challenger failed "
                "the quality gate."
            )


            print(
                "\nThe existing champion "
                "remains active."
            )


            return


        # =================================================
        # STAGE 3
        # REGISTER CHALLENGER
        # =================================================

        update_state(
            state,

            current_stage=
                "REGISTERING_CHALLENGER",
        )


        run_command(
            "STAGE 3 - REGISTER CHALLENGER",
            REGISTER_COMMAND,
        )


        # =================================================
        # STAGE 4
        # PROMOTE
        # =================================================

        update_state(
            state,

            current_stage=
                "PROMOTING_CHALLENGER",

            promotion_attempted=
                True,
        )


        run_command(
            "STAGE 4 - PROMOTE CHALLENGER",
            PROMOTE_COMMAND,
        )


        update_state(
            state,

            promotion_completed=
                True,
        )


        # =================================================
        # STAGE 5
        # VERIFY PROMOTION
        # =================================================

        update_state(
            state,

            current_stage=
                "VERIFYING_PROMOTION",
        )


        run_command(
            "STAGE 5 - VERIFY PROMOTION",
            VERIFY_COMMAND,
        )


        update_state(
            state,

            verification_completed=
                True,
        )


        # =================================================
        # READ FINAL DEPLOYMENT STATE
        # =================================================

        deployment = (
            load_json(
                DEPLOYMENT_STATE_PATH
            )
        )


        completed_at = (
            utc_now()
        )


        duration = (
            time.perf_counter()
            -
            start_time
        )


        # =================================================
        # SUCCESS STATE
        # =================================================

        update_state(
            state,

            status=
                "SELF_HEALED",

            current_stage=
                "FINISHED",

            completed_at=
                completed_at,

            duration_seconds=
                round(
                    duration,
                    2,
                ),

            champion_version=
                (
                    deployment.get(
                        "champion_version"
                    )
                    if deployment
                    else None
                ),

            previous_champion_version=
                (
                    deployment.get(
                        "previous_champion_version"
                    )
                    if deployment
                    else None
                ),

            rollback_available=
                (
                    deployment.get(
                        "rollback_available"
                    )
                    if deployment
                    else False
                ),
        )


        print(
            "\n"
            "===================================================="
        )

        print(
            " SELF-HEALING PIPELINE COMPLETE"
        )

        print(
            "===================================================="
        )


        print(
            "\nResult:"
        )

        print(
            "SELF_HEALED"
        )


        if deployment:

            print(
                "\nActive champion:"
            )

            print(
                "Version "
                f"{deployment.get('champion_version')}"
            )


            print(
                "\nPrevious champion:"
            )

            print(
                "Version "
                f"{deployment.get('previous_champion_version')}"
            )


            print(
                "\nRollback available:"
            )

            print(
                deployment.get(
                    "rollback_available"
                )
            )


        print(
            "\nDuration:"
        )

        print(
            f"{duration:.2f} seconds"
        )


    # =====================================================
    # FAILURE HANDLING
    # =====================================================

    except Exception as error:

        duration = (
            time.perf_counter()
            -
            start_time
        )


        failure_stage = (
            state.get(
                "current_stage"
            )
        )


        update_state(
            state,

            status=
                "FAILED",

            failure_stage=
                failure_stage,

            error=
                str(error),

            completed_at=
                utc_now(),

            duration_seconds=
                round(
                    duration,
                    2,
                ),
        )


        print(
            "\n"
            "===================================================="
        )

        print(
            " SELF-HEALING PIPELINE FAILED"
        )

        print(
            "===================================================="
        )


        print(
            "\nFailure stage:"
        )

        print(
            failure_stage
        )


        print(
            "\nError:"
        )

        print(
            error
        )


        sys.exit(1)


# =========================================================
# EXECUTE
# =========================================================

if __name__ == "__main__":
    main()