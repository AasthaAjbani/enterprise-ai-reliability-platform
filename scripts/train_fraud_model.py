from pathlib import Path
import json

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from mlflow.models import infer_signature

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ---------------------------------------------------------
# 1. PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "transactions_reference.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

MODEL_FILE = (
    MODEL_DIR
    / "fraud_model.joblib"
)

METRICS_FILE = (
    MODEL_DIR
    / "baseline_metrics.json"
)

MLFLOW_DB_FILE = (
    PROJECT_ROOT
    / "mlflow.db"
)


# ---------------------------------------------------------
# 2. MLFLOW CONFIGURATION
# ---------------------------------------------------------

MLFLOW_TRACKING_URI = (
    f"sqlite:///{MLFLOW_DB_FILE.as_posix()}"
)

EXPERIMENT_NAME = (
    "Enterprise AI Reliability - Fraud Detection"
)

REGISTERED_MODEL_NAME = (
    "FraudDetectionModel"
)


mlflow.set_tracking_uri(
    MLFLOW_TRACKING_URI
)

mlflow.set_registry_uri(
    MLFLOW_TRACKING_URI
)

mlflow.set_experiment(
    EXPERIMENT_NAME
)


# ---------------------------------------------------------
# 3. LOAD DATA
# ---------------------------------------------------------

print(
    "\nLoading reference dataset..."
)

data = pd.read_csv(
    DATA_FILE
)

print(
    "Dataset loaded successfully."
)

print(
    f"Dataset shape: {data.shape}"
)


# ---------------------------------------------------------
# 4. FEATURES AND TARGET
# ---------------------------------------------------------

TARGET_COLUMN = (
    "is_fraud"
)

DROP_COLUMNS = [
    "transaction_id",
    TARGET_COLUMN,
]


X = data.drop(
    columns=DROP_COLUMNS
)

y = data[
    TARGET_COLUMN
]


# ---------------------------------------------------------
# 5. FEATURE TYPES
# ---------------------------------------------------------

categorical_features = [
    "payment_method",
    "device_type",
    "customer_location",
]


numerical_features = [
    "customer_age",
    "transaction_amount",
    "transaction_hour",
    "account_age_days",
    "previous_transactions",
    "failed_transactions_last_24h",
    "is_international",
]


# ---------------------------------------------------------
# 6. TRAIN / TEST SPLIT
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
)


print(
    "\nTrain/Test split completed."
)

print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples: {len(X_test)}"
)


# ---------------------------------------------------------
# 7. MODEL PARAMETERS
# ---------------------------------------------------------

MODEL_PARAMETERS = {
    "n_estimators": 200,
    "random_state": 42,
    "class_weight": "balanced",
    "n_jobs": -1,
}


# ---------------------------------------------------------
# 8. PREPROCESSOR
# ---------------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features,
        ),
        (
            "numerical",
            "passthrough",
            numerical_features,
        ),
    ]
)


# ---------------------------------------------------------
# 9. RANDOM FOREST MODEL
# ---------------------------------------------------------

model = RandomForestClassifier(
    **MODEL_PARAMETERS
)


# ---------------------------------------------------------
# 10. COMPLETE PIPELINE
# ---------------------------------------------------------

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            model,
        ),
    ]
)


# ---------------------------------------------------------
# 11. CREATE MODEL DIRECTORY
# ---------------------------------------------------------

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# 12. START MLFLOW RUN
# ---------------------------------------------------------

print(
    "\nStarting MLflow experiment..."
)


with mlflow.start_run(
    run_name="RandomForest_Baseline"
) as run:

    # -----------------------------------------------------
    # LOG PARAMETERS
    # -----------------------------------------------------

    mlflow.log_params(
        {
            "model_type":
                "RandomForestClassifier",

            "n_estimators":
                MODEL_PARAMETERS[
                    "n_estimators"
                ],

            "random_state":
                MODEL_PARAMETERS[
                    "random_state"
                ],

            "class_weight":
                MODEL_PARAMETERS[
                    "class_weight"
                ],

            "test_size":
                0.20,

            "training_rows":
                len(X_train),

            "testing_rows":
                len(X_test),

            "categorical_feature_count":
                len(
                    categorical_features
                ),

            "numerical_feature_count":
                len(
                    numerical_features
                ),
        }
    )


    # -----------------------------------------------------
    # TRAIN MODEL
    # -----------------------------------------------------

    print(
        "\nTraining fraud detection model..."
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    print(
        "Model training completed."
    )


    # -----------------------------------------------------
    # MAKE PREDICTIONS
    # -----------------------------------------------------

    predictions = pipeline.predict(
        X_test
    )


    # -----------------------------------------------------
    # CALCULATE METRICS
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
    )


    # -----------------------------------------------------
    # LOG METRICS TO MLFLOW
    # -----------------------------------------------------

    mlflow.log_metrics(
        {
            "accuracy":
                float(accuracy),

            "precision":
                float(precision),

            "recall":
                float(recall),

            "f1_score":
                float(f1),

            "reference_fraud_rate":
                float(
                    y.mean()
                ),
        }
    )


    # -----------------------------------------------------
    # SAVE BASELINE METRICS
    # -----------------------------------------------------

    baseline_metrics = {
        "accuracy":
            float(accuracy),

        "precision":
            float(precision),

        "recall":
            float(recall),

        "f1":
            float(f1),

        "confusion_matrix":
            matrix.tolist(),
    }


    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            baseline_metrics,
            file,
            indent=4,
        )


    # -----------------------------------------------------
    # SAVE LOCAL MODEL
    # -----------------------------------------------------

    joblib.dump(
        pipeline,
        MODEL_FILE,
    )


    # -----------------------------------------------------
    # LOG METRICS FILE AS ARTIFACT
    # -----------------------------------------------------

    mlflow.log_artifact(
        str(
            METRICS_FILE
        ),
        artifact_path="evaluation",
    )


    # -----------------------------------------------------
    # MODEL SIGNATURE
    # -----------------------------------------------------

    input_example = (
        X_test
        .head(5)
        .copy()
    )


    example_predictions = (
        pipeline.predict(
            input_example
        )
    )


    signature = (
        infer_signature(
            input_example,
            example_predictions,
        )
    )


    # -----------------------------------------------------
    # LOG + REGISTER MODEL
    # -----------------------------------------------------

    model_info = (
        mlflow.sklearn.log_model(
            sk_model=pipeline,

            name="fraud_model",

            registered_model_name=(
                REGISTERED_MODEL_NAME
            ),

            signature=signature,

            input_example=(
                input_example
            ),

            serialization_format=(
                "cloudpickle"
            ),
        )
    )


    # -----------------------------------------------------
    # TAGS
    # -----------------------------------------------------

    mlflow.set_tags(
        {
            "project":
                "Enterprise AI Reliability Platform",

            "model_purpose":
                "Fraud Detection",

            "model_stage":
                "baseline",

            "dataset":
                "synthetic_ecommerce_transactions",
        }
    )


    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------

    run_id = (
        run.info.run_id
    )


    print("\n")
    print("=" * 70)

    print(
        "BASELINE MODEL PERFORMANCE"
    )

    print("=" * 70)


    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1 Score : {f1:.4f}"
    )


    print(
        "\nClassification Report:\n"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )


    print(
        "Confusion Matrix:"
    )

    print(
        matrix
    )


    print("\n")
    print("=" * 70)

    print(
        "MLFLOW RUN INFORMATION"
    )

    print("=" * 70)

    print(
        f"Experiment: "
        f"{EXPERIMENT_NAME}"
    )

    print(
        f"Run ID: "
        f"{run_id}"
    )

    print(
        f"Registered Model: "
        f"{REGISTERED_MODEL_NAME}"
    )

    print(
        f"MLflow Tracking URI: "
        f"{MLFLOW_TRACKING_URI}"
    )


print("\n")
print("=" * 70)

print(
    "TRAINING COMPLETED SUCCESSFULLY"
)

print("=" * 70)


print(
    f"\nLocal model: "
    f"{MODEL_FILE}"
)

print(
    f"Baseline metrics: "
    f"{METRICS_FILE}"
)