from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.config import PROJECT_ROOT
from app.ml.features import DEFAULT_FEATURE_COLUMNS, dataframe_to_feature_matrix

SAMPLE_SENSOR_DATA_PATH = PROJECT_ROOT / "data" / "sample" / "sample_sensor_data.csv"
SAMPLE_FEEDBACK_DATA_PATH = PROJECT_ROOT / "data" / "sample" / "sample_feedback.csv"


def load_sample_sensor_data(sample_path: str | Path | None = None) -> pd.DataFrame:
    """Load MVP sensor data for local model training.

    Later this function can be replaced or expanded to read from a database,
    historian, SAP imports, alarms, feedback, and technician notes.
    """

    path = Path(sample_path or SAMPLE_SENSOR_DATA_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Sample sensor data was not found at {path}")

    dataframe = pd.read_csv(path)
    missing = [column for column in ["timestamp", "asset_id", "asset_code", *DEFAULT_FEATURE_COLUMNS] if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Sample sensor data is missing column(s): {', '.join(missing)}")
    return dataframe


def build_anomaly_detection_dataset(sample_path: str | Path | None = None) -> pd.DataFrame:
    """Build the Isolation Forest training dataset from available sensor data."""

    dataframe = load_sample_sensor_data(sample_path)
    dataframe_to_feature_matrix(dataframe, DEFAULT_FEATURE_COLUMNS)
    return dataframe.loc[:, DEFAULT_FEATURE_COLUMNS].astype(float)


def build_failure_classification_dataset_placeholder() -> dict:
    """Placeholder for future Random Forest/XGBoost failure-mode training data."""

    return {
        "status": "not_ready",
        "target": "failure_mode",
        "message": "Failure classification will require labeled failures, causes, actions, and work orders.",
    }


def build_rul_dataset_placeholder() -> dict:
    """Placeholder for future Remaining Useful Life model training data."""

    return {
        "status": "not_ready",
        "target": "remaining_useful_life_days",
        "message": "RUL training will require time-to-failure labels and long sensor histories.",
    }


def load_feedback_training_data(feedback_path: str | Path | None = None) -> pd.DataFrame:
    """Load technician feedback for future model/recommendation learning.

    The MVP uses CSV feedback. Future retraining can replace this with database
    queries while keeping the function contract stable for training builders.
    """

    path = Path(feedback_path or SAMPLE_FEEDBACK_DATA_PATH)
    if not path.exists():
        return pd.DataFrame(
            columns=[
                "feedback_id",
                "asset_id",
                "asset_code",
                "prediction_id",
                "feedback_date",
                "was_prediction_correct",
                "actual_failure_happened",
                "actual_failure_mode",
                "action_taken",
                "timing_feedback",
                "technician_comment",
            ]
        )
    return pd.read_csv(path)
