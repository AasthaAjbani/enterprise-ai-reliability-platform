from pathlib import Path

import joblib
import pandas as pd

from app.monitoring.anomaly_detector import (
    train_anomaly_detector,
)


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REFERENCE_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "transactions_reference.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

ANOMALY_MODEL_FILE = (
    MODEL_DIR
    / "anomaly_detector.joblib"
)

SCALER_FILE = (
    MODEL_DIR
    / "anomaly_scaler.joblib"
)


# ---------------------------------------------------------
# 2. LOAD REFERENCE DATA
# ---------------------------------------------------------

print(
    "\nLoading reference data..."
)

reference_data = pd.read_csv(
    REFERENCE_DATA_FILE
)

print(
    f"Reference rows loaded: "
    f"{len(reference_data)}"
)


# ---------------------------------------------------------
# 3. TRAIN ANOMALY DETECTOR
# ---------------------------------------------------------

print(
    "\nTraining Isolation Forest..."
)

detector, scaler = (
    train_anomaly_detector(
        reference_data
    )
)

print(
    "Anomaly detector trained successfully."
)


# ---------------------------------------------------------
# 4. CREATE MODEL DIRECTORY
# ---------------------------------------------------------

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# 5. SAVE ARTIFACTS
# ---------------------------------------------------------

joblib.dump(
    detector,
    ANOMALY_MODEL_FILE,
)

joblib.dump(
    scaler,
    SCALER_FILE,
)


print(
    "\nArtifacts saved successfully."
)

print(
    f"Detector: {ANOMALY_MODEL_FILE}"
)

print(
    f"Scaler  : {SCALER_FILE}"
)