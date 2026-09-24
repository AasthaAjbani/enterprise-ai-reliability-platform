from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.services.reliability_service import (
    generate_reliability_report,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODELS_DIR = PROJECT_ROOT / "models"

SNAPSHOT_FILE = (
    MODELS_DIR
    / "reliability_snapshot.json"
)

TEMP_SNAPSHOT_FILE = (
    MODELS_DIR
    / "reliability_snapshot.tmp.json"
)


# ============================================================
# JSON CLEANER
# ============================================================

def clean_for_json(value: Any) -> Any:
    """
    Convert Pandas / NumPy / non-finite values into
    standard JSON-safe Python values.
    """

    # --------------------------------------------------------
    # None
    # --------------------------------------------------------

    if value is None:
        return None


    # --------------------------------------------------------
    # Dictionaries
    # --------------------------------------------------------

    if isinstance(value, dict):
        return {
            str(key): clean_for_json(item)
            for key, item in value.items()
        }


    # --------------------------------------------------------
    # Lists / tuples / sets
    # --------------------------------------------------------

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            clean_for_json(item)
            for item in value
        ]


    # --------------------------------------------------------
    # Pandas DataFrame
    # --------------------------------------------------------

    if isinstance(
        value,
        pd.DataFrame,
    ):
        return clean_for_json(
            value.to_dict(
                orient="records"
            )
        )


    # --------------------------------------------------------
    # Pandas Series
    # --------------------------------------------------------

    if isinstance(
        value,
        pd.Series,
    ):
        return clean_for_json(
            value.to_dict()
        )


    # --------------------------------------------------------
    # Pandas Timestamp
    # --------------------------------------------------------

    if isinstance(
        value,
        pd.Timestamp,
    ):
        return value.isoformat()


    # --------------------------------------------------------
    # NumPy arrays
    # --------------------------------------------------------

    if isinstance(
        value,
        np.ndarray,
    ):
        return clean_for_json(
            value.tolist()
        )


    # --------------------------------------------------------
    # NumPy scalar values
    # --------------------------------------------------------

    if isinstance(
        value,
        np.generic,
    ):
        return clean_for_json(
            value.item()
        )


    # --------------------------------------------------------
    # Float values
    #
    # JSON should not contain NaN or Infinity.
    # --------------------------------------------------------

    if isinstance(
        value,
        float,
    ):
        if not math.isfinite(
            value
        ):
            return None

        return value


    # --------------------------------------------------------
    # Primitive JSON values
    # --------------------------------------------------------

    if isinstance(
        value,
        (
            str,
            int,
            bool,
        ),
    ):
        return value


    # --------------------------------------------------------
    # Path objects
    # --------------------------------------------------------

    if isinstance(
        value,
        Path,
    ):
        return str(
            value
        )


    # --------------------------------------------------------
    # Final safe fallback
    # --------------------------------------------------------

    return str(
        value
    )


# ============================================================
# GENERATE SNAPSHOT
# ============================================================

def generate_snapshot() -> dict:
    """
    Run the full reliability analysis once and convert
    the result into a JSON-safe snapshot.
    """

    print()
    print(
        "=" * 70
    )

    print(
        "GENERATING RELIABILITY SNAPSHOT"
    )

    print(
        "=" * 70
    )


    print(
        "\nRunning reliability analysis..."
    )


    report = (
        generate_reliability_report()
    )


    print(
        "Reliability analysis complete."
    )


    snapshot = clean_for_json(
        report
    )


    # --------------------------------------------------------
    # Add snapshot metadata without changing existing report
    # fields expected by the frontend.
    # --------------------------------------------------------

    if isinstance(
        snapshot,
        dict,
    ):

        snapshot[
            "snapshot_metadata"
        ] = {
            "generated_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),

            "source": (
                "reliability_snapshot"
            ),

            "mode": (
                "precomputed"
            ),
        }


    return snapshot


# ============================================================
# SAVE SNAPSHOT
# ============================================================

def save_snapshot(
    snapshot: dict,
) -> None:

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # --------------------------------------------------------
    # Write to temporary file first.
    #
    # This prevents a partially written JSON file from being
    # served if something fails while writing.
    # --------------------------------------------------------

    with TEMP_SNAPSHOT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            snapshot,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


    # --------------------------------------------------------
    # Atomic replacement
    # --------------------------------------------------------

    os.replace(
        TEMP_SNAPSHOT_FILE,
        SNAPSHOT_FILE,
    )


    print(
        "\nSnapshot saved successfully:"
    )

    print(
        SNAPSHOT_FILE
    )


# ============================================================
# MAIN
# ============================================================

def main():

    snapshot = (
        generate_snapshot()
    )


    save_snapshot(
        snapshot
    )


    print()

    print(
        "=" * 70
    )

    print(
        "SNAPSHOT GENERATION COMPLETE"
    )

    print(
        "=" * 70
    )


    print(
        "\nThe expensive monitoring pipeline "
        "has been executed once."
    )

    print(
        "The API will later serve this JSON "
        "instead of recalculating everything "
        "for every dashboard request."
    )

    print()


if __name__ == "__main__":
    main()