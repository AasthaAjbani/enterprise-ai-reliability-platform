import json

from fastapi import APIRouter, HTTPException

from app.services.reliability_snapshot_service import (
    load_reliability_snapshot,
)


# ---------------------------------------------------------
# 1. CREATE ROUTER
# ---------------------------------------------------------

router = APIRouter(
    prefix="/api",
    tags=["AI Reliability"],
)


# ---------------------------------------------------------
# 2. SAFE SNAPSHOT LOADER
# ---------------------------------------------------------

def get_snapshot():
    """
    Load the precomputed reliability snapshot.

    The API no longer reruns the complete ML monitoring
    pipeline for every request.
    """

    try:

        return load_reliability_snapshot()

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=503,
            detail=(
                "Reliability snapshot is not available. "
                "Generate it with: "
                "python -m scripts.generate_reliability_snapshot"
            ),
        ) from error

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Reliability snapshot contains invalid JSON."
            ),
        ) from error

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load reliability snapshot."
            ),
        ) from error


# ---------------------------------------------------------
# 3. COMPLETE RELIABILITY REPORT
# ---------------------------------------------------------

@router.get("/reliability")
def get_reliability_report():

    report = get_snapshot()


    response = {

        # -------------------------------------------------
        # OVERALL STATUS
        # -------------------------------------------------

        "overall_status":
            report[
                "overall_status"
            ],


        # -------------------------------------------------
        # DATA QUALITY
        # -------------------------------------------------

        "data_quality":
            report[
                "data_quality"
            ],


        # -------------------------------------------------
        # DATA DRIFT
        # -------------------------------------------------

        "data_drift": {

            "status":
                report[
                    "data_drift"
                ][
                    "status"
                ],

            "features":
                report[
                    "data_drift"
                ][
                    "report"
                ],
        },


        # -------------------------------------------------
        # MODEL PERFORMANCE
        # -------------------------------------------------

        "model_performance": {

            "status":
                report[
                    "model_performance"
                ][
                    "status"
                ],

            "reference":
                report[
                    "model_performance"
                ][
                    "reference_metrics"
                ],

            "production":
                report[
                    "model_performance"
                ][
                    "production_metrics"
                ],

            "performance_drop":
                report[
                    "model_performance"
                ][
                    "performance_drop"
                ],
        },


        # -------------------------------------------------
        # ANOMALY DETECTION
        # -------------------------------------------------

        "anomaly_detection": {

            "status":
                report[
                    "anomaly_detection"
                ][
                    "status"
                ],

            "total_transactions":
                report[
                    "anomaly_detection"
                ][
                    "total_transactions"
                ],

            "anomaly_count":
                report[
                    "anomaly_detection"
                ][
                    "anomaly_count"
                ],

            "anomaly_percentage":
                report[
                    "anomaly_detection"
                ][
                    "anomaly_percentage"
                ],

            "top_anomalies":
                report[
                    "anomaly_detection"
                ][
                    "top_anomalies"
                ],
        },


        # -------------------------------------------------
        # ROOT CAUSES
        # -------------------------------------------------

        "root_causes":
            report[
                "root_cause"
            ],


        # -------------------------------------------------
        # RECOMMENDATION
        # -------------------------------------------------

        "recommendation":
            report[
                "recommendation"
            ],


        # -------------------------------------------------
        # SNAPSHOT INFO
        # -------------------------------------------------

        "snapshot_metadata":
            report.get(
                "snapshot_metadata",
                {},
            ),
    }


    return response


# ---------------------------------------------------------
# 4. DATA QUALITY ENDPOINT
# ---------------------------------------------------------

@router.get("/data-quality")
def get_data_quality():

    report = get_snapshot()


    return report[
        "data_quality"
    ]


# ---------------------------------------------------------
# 5. DATA DRIFT ENDPOINT
# ---------------------------------------------------------

@router.get("/drift")
def get_drift_report():

    report = get_snapshot()


    response = {

        "status":
            report[
                "data_drift"
            ][
                "status"
            ],

        "features":
            report[
                "data_drift"
            ][
                "report"
            ],
    }


    return response


# ---------------------------------------------------------
# 6. MODEL PERFORMANCE ENDPOINT
# ---------------------------------------------------------

@router.get("/performance")
def get_performance():

    report = get_snapshot()


    performance = (
        report[
            "model_performance"
        ]
    )


    response = {

        "status":
            performance[
                "status"
            ],

        "baseline":
            performance[
                "reference_metrics"
            ],

        "production":
            performance[
                "production_metrics"
            ],

        "performance_drop":
            performance[
                "performance_drop"
            ],
    }


    return response


# ---------------------------------------------------------
# 7. ROOT CAUSE ENDPOINT
# ---------------------------------------------------------

@router.get("/root-causes")
def get_root_causes():

    report = get_snapshot()


    response = {

        "root_causes":
            report[
                "root_cause"
            ],

        "recommendation":
            report[
                "recommendation"
            ],
    }


    return response


# ---------------------------------------------------------
# 8. ANOMALY DETECTION ENDPOINT
# ---------------------------------------------------------

@router.get("/anomalies")
def get_anomalies():

    report = get_snapshot()


    anomaly_report = (
        report[
            "anomaly_detection"
        ]
    )


    response = {

        "status":
            anomaly_report[
                "status"
            ],

        "total_transactions":
            anomaly_report[
                "total_transactions"
            ],

        "anomaly_count":
            anomaly_report[
                "anomaly_count"
            ],

        "anomaly_percentage":
            anomaly_report[
                "anomaly_percentage"
            ],

        "top_anomalies":
            anomaly_report[
                "top_anomalies"
            ],
    }


    return response