from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent.parent

SNAPSHOT_FILE = (
    PROJECT_ROOT
    / "models"
    / "reliability_snapshot.json"
)


# ============================================================
# SIMPLE IN-MEMORY CACHE
# ============================================================

_cached_snapshot: dict[str, Any] | None = None
_cached_modified_time: float | None = None


# ============================================================
# LOAD SNAPSHOT
# ============================================================

def load_reliability_snapshot() -> dict[str, Any]:
    """
    Load the precomputed reliability snapshot.

    The JSON file is only read again when its modification
    time changes. This keeps API requests lightweight while
    still allowing a newly generated snapshot to be picked up.
    """

    global _cached_snapshot
    global _cached_modified_time


    # --------------------------------------------------------
    # Verify snapshot exists
    # --------------------------------------------------------

    if not SNAPSHOT_FILE.exists():

        raise FileNotFoundError(
            "Reliability snapshot does not exist. "
            "Generate it with:\n"
            "python -m scripts.generate_reliability_snapshot"
        )


    # --------------------------------------------------------
    # Check file modification time
    # --------------------------------------------------------

    modified_time = (
        SNAPSHOT_FILE
        .stat()
        .st_mtime
    )


    # --------------------------------------------------------
    # Return cached snapshot when file has not changed
    # --------------------------------------------------------

    if (
        _cached_snapshot is not None
        and
        _cached_modified_time
        ==
        modified_time
    ):

        return _cached_snapshot


    # --------------------------------------------------------
    # Read snapshot from disk
    # --------------------------------------------------------

    with SNAPSHOT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        snapshot = json.load(
            file
        )


    # --------------------------------------------------------
    # Validate basic structure
    # --------------------------------------------------------

    if not isinstance(
        snapshot,
        dict,
    ):

        raise ValueError(
            "Reliability snapshot must contain "
            "a JSON object at the top level."
        )


    # --------------------------------------------------------
    # Update cache
    # --------------------------------------------------------

    _cached_snapshot = snapshot

    _cached_modified_time = (
        modified_time
    )


    return snapshot


# ============================================================
# GET INDIVIDUAL SNAPSHOT SECTION
# ============================================================

def get_snapshot_section(
    section_name: str,
) -> Any:
    """
    Return one section of the reliability snapshot.
    """

    snapshot = (
        load_reliability_snapshot()
    )


    if section_name not in snapshot:

        raise KeyError(
            f"Section '{section_name}' "
            "does not exist in reliability snapshot. "
            f"Available sections: "
            f"{list(snapshot.keys())}"
        )


    return snapshot[
        section_name
    ]


# ============================================================
# SNAPSHOT METADATA
# ============================================================

def get_snapshot_metadata() -> dict[str, Any]:
    """
    Return metadata describing when/how the snapshot
    was generated.
    """

    snapshot = (
        load_reliability_snapshot()
    )


    metadata = snapshot.get(
        "snapshot_metadata",
        {},
    )


    if not isinstance(
        metadata,
        dict,
    ):

        return {}


    return metadata