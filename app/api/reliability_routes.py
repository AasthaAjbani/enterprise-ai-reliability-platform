import math

import numpy as np
import pandas as pd

from fastapi import APIRouter

from app.services.reliability_service import (
    generate_reliability_report,
)


# ---------------------------------------------------------
# 1. CREATE ROUTER
# ---------------------------------------------------------

router = APIRouter(
    prefix="/api",
    tags=["AI Reliability"],
)


# ---------------------------------------------------------
# 2. JSON CLEANER
# ---------------------------------------------------------

def clean_for_json(value):
    """
    Converts Pandas and NumPy values into
    standard Python values that FastAPI
    can safely return as JSON.
    """

    # Pandas DataFrame
    if isinstance(value, pd.DataFrame):

        records = value.to_dict(
            orient="records"
        )

        return clean_for_json(
            records
        )


    # Pandas Series
    if isinstance(value, pd.Series):

        return clean_for_json(
            value.to_dict()
        )


    # Dictionary
    if isinstance(value, dict):

        return {
            key: clean_for_json(item)
            for key, item in value.items()
        }


    # List or Tuple
    if isinstance(
        value,
        (list, tuple),
    ):

        return [
            clean_for_json(item)
            for item in value
        ]


    # NumPy Array
    if isinstance(
        value,
        np.ndarray,
    ):

        return clean_for_json(
            value.tolist()
        )


    # NumPy Integer
    if isinstance(
        value,
        np.integer,
    ):

        return int(value)


    # NumPy Float
    if isinstance(
        value,
        np.floating,
    ):

        value = float(value)

        if (
            math.isnan(value)
            or math.isinf(value)
        ):
            return None

        return value


    # Standard Python Float
    if isinstance(
        value,
        float,
    ):

        if (
            math.isnan(value)
            or math.isinf(value)
        ):
            return None

        return value


    return value


# ---------------------------------------------------------
# 3. COMPLETE RELIABILITY REPORT
# ---------------------------------------------------------

@router.get("/reliability")
def get_reliability_report():

    report = (
        generate_reliability_report()
    )


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
    }


    return clean_for_json(
        response
    )


# ---------------------------------------------------------
# 4. DATA QUALITY ENDPOINT
# ---------------------------------------------------------

@router.get("/data-quality")
def get_data_quality():

    report = (
        generate_reliability_report()
    )


    response = (
        report[
            "data_quality"
        ]
    )


    return clean_for_json(
        response
    )


# ---------------------------------------------------------
# 5. DATA DRIFT ENDPOINT
# ---------------------------------------------------------

@router.get("/drift")
def get_drift_report():

    report = (
        generate_reliability_report()
    )


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


    return clean_for_json(
        response
    )


# ---------------------------------------------------------
# 6. MODEL PERFORMANCE ENDPOINT
# ---------------------------------------------------------

@router.get("/performance")
def get_performance():

    report = (
        generate_reliability_report()
    )


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


    return clean_for_json(
        response
    )


# ---------------------------------------------------------
# 7. ROOT CAUSE ENDPOINT
# ---------------------------------------------------------

@router.get("/root-causes")
def get_root_causes():

    report = (
        generate_reliability_report()
    )


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


    return clean_for_json(
        response
    )


# ---------------------------------------------------------
# 8. ANOMALY DETECTION ENDPOINT
# ---------------------------------------------------------

@router.get("/anomalies")
def get_anomalies():

    report = (
        generate_reliability_report()
    )


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


    return clean_for_json(
        response
    )