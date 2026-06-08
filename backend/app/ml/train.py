from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import get_settings
from app.ml.features import DEFAULT_FEATURE_COLUMNS
from app.ml.training_data_builder import build_anomaly_detection_dataset, load_sample_sensor_data
from app.ml.pipelines.isolation_forest_pipeline import IsolationForestMaintenanceModel

MODEL_FILENAME = "isolation_forest_v1.joblib"
SCALER_FILENAME = "scaler_v1.joblib"
MODEL_VERSION = "1.0.0"


def train_isolation_forest_from_sample_data(sample_path: str | Path | None = None) -> dict:
    """Train the MVP Isolation Forest model from sample sensor data."""
    settings = get_settings()
    raw_data = load_sample_sensor_data(sample_path)
    training_data = build_anomaly_detection_dataset(sample_path)

    model = IsolationForestMaintenanceModel.train(
        training_data,
        feature_columns=DEFAULT_FEATURE_COLUMNS,
        version=MODEL_VERSION,
    )

    settings.saved_models_dir.mkdir(parents=True, exist_ok=True)
    model_path = settings.saved_models_dir / MODEL_FILENAME
    scaler_path = settings.saved_models_dir / SCALER_FILENAME
    model.save(model_path, scaler_path=scaler_path)

    metadata = {
        "active_model": MODEL_FILENAME,
        "scaler": SCALER_FILENAME,
        "model_type": model.model_type,
        "version": MODEL_VERSION,
        "trained_at": datetime.now(UTC).isoformat(),
        "features": DEFAULT_FEATURE_COLUMNS,
        "target_type": "anomaly_detection",
        "status": "trained",
    }
    settings.active_model_metadata_file.parent.mkdir(parents=True, exist_ok=True)
    settings.active_model_metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(
        "Training completed successfully. "
        f"Rows={len(raw_data)} Model={model_path} Scaler={scaler_path} "
        f"Metadata={settings.active_model_metadata_file}"
    )
    return metadata


if __name__ == "__main__":
    train_isolation_forest_from_sample_data()
