from __future__ import annotations

import json
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


MODELS_DIR = (
    PROJECT_ROOT
    / "models"
)


DEPLOYMENT_STATE_PATH = (
    MODELS_DIR
    / "deployment_state.json"
)


BASELINE_METRICS_PATH = (
    MODELS_DIR
    / "baseline_metrics.json"
)


# =========================================================
# REQUIRED METRICS
# =========================================================

REQUIRED_METRICS = [
    "accuracy",
    "precision",
    "recall",
    "f1",
]


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

        return json.load(
            file
        )


# =========================================================
# NORMALIZE METRICS
# =========================================================

def normalize_metrics(
    metrics,
):

    if not isinstance(
        metrics,
        dict,
    ):

        return None


    normalized = {}


    for metric in REQUIRED_METRICS:

        if metric not in metrics:

            return None


        try:

            normalized[
                metric
            ] = float(
                metrics[
                    metric
                ]
            )


        except (
            TypeError,
            ValueError,
        ):

            return None


    return normalized


# =========================================================
# LOAD ORIGINAL BASELINE
# =========================================================

def load_original_baseline():

    baseline = (
        load_json(
            BASELINE_METRICS_PATH
        )
    )


    if baseline is None:

        raise FileNotFoundError(
            "\nOriginal baseline metrics not found:\n"
            f"{BASELINE_METRICS_PATH}"
        )


    metrics = (
        normalize_metrics(
            baseline
        )
    )


    if metrics is None:

        raise ValueError(
            "\nOriginal baseline metrics are invalid."
        )


    return metrics


# =========================================================
# GET ACTIVE MODEL BASELINE
# =========================================================

def get_active_model_baseline():

    deployment_state = (
        load_json(
            DEPLOYMENT_STATE_PATH
        )
    )


    # -----------------------------------------------------
    # Deployment metadata
    # -----------------------------------------------------

    champion_version = None

    previous_champion_version = None


    if isinstance(
        deployment_state,
        dict,
    ):

        champion_version = (
            deployment_state.get(
                "champion_version"
            )
        )


        previous_champion_version = (
            deployment_state.get(
                "previous_champion_version"
            )
        )


    # =====================================================
    # PRIMARY SOURCE
    #
    # Baseline saved when the current champion was promoted.
    #
    # IMPORTANT:
    # We intentionally DO NOT read challenger_comparison.json
    # here because that file is mutable and gets overwritten
    # every time a new challenger is trained.
    # =====================================================

    if isinstance(
        deployment_state,
        dict,
    ):

        accepted_baseline = (
            deployment_state.get(
                "accepted_baseline"
            )
        )


        if isinstance(
            accepted_baseline,
            dict,
        ):

            stored_metrics = (
                accepted_baseline.get(
                    "metrics",
                    {},
                )
            )


            metrics = (
                normalize_metrics(
                    stored_metrics
                )
            )


            if metrics is not None:

                return {

                    "source":
                        accepted_baseline.get(
                            "source",
                            "deployment_state",
                        ),

                    "champion_version":
                        champion_version,

                    "previous_champion_version":
                        previous_champion_version,

                    "validation_type":
                        accepted_baseline.get(
                            "validation_type",
                            "held_out_production_validation",
                        ),

                    "validation_fraction":
                        accepted_baseline.get(
                            "validation_fraction"
                        ),

                    # -------------------------------------
                    # Dataset used when champion baseline
                    # was accepted.
                    # -------------------------------------

                    "production_data_path":
                        accepted_baseline.get(
                            "production_data_path"
                        ),

                    # -------------------------------------
                    # Needed to recreate the exact
                    # train/validation split.
                    # -------------------------------------

                    "random_state":
                        accepted_baseline.get(
                            "random_state"
                        ),

                    "metrics":
                        metrics,
                }


    # =====================================================
    # FALLBACK SOURCE
    #
    # Used before the first promoted champion has an
    # accepted baseline stored in deployment_state.json.
    # =====================================================

    original_metrics = (
        load_original_baseline()
    )


    return {

        "source":
            "original_training_baseline",

        "champion_version":
            champion_version,

        "previous_champion_version":
            previous_champion_version,

        "validation_type":
            "original_model_validation",

        "validation_fraction":
            None,

        "production_data_path":
            None,

        "random_state":
            None,

        "metrics":
            original_metrics,
    }


# =========================================================
# DISPLAY BASELINE
# =========================================================

def main():

    baseline = (
        get_active_model_baseline()
    )


    print()
    print(
        "=" * 70
    )

    print(
        "ACTIVE MODEL BASELINE"
    )

    print(
        "=" * 70
    )


    print(
        "\nSource:",
        baseline.get(
            "source"
        ),
    )


    print(
        "Champion version:",
        baseline.get(
            "champion_version"
        ),
    )


    print(
        "Previous champion version:",
        baseline.get(
            "previous_champion_version"
        ),
    )


    print(
        "Validation type:",
        baseline.get(
            "validation_type"
        ),
    )


    print(
        "Validation fraction:",
        baseline.get(
            "validation_fraction"
        ),
    )


    print(
        "Production data path:",
        baseline.get(
            "production_data_path"
        ),
    )


    print(
        "Random state:",
        baseline.get(
            "random_state"
        ),
    )


    print(
        "\nMetrics:"
    )


    metrics = (
        baseline[
            "metrics"
        ]
    )


    for metric in REQUIRED_METRICS:

        print(
            f"  {metric:<10} "
            f"{metrics[metric]:.4f}"
        )


    print()


# =========================================================
# EXECUTE
# =========================================================

if __name__ == "__main__":
    main()