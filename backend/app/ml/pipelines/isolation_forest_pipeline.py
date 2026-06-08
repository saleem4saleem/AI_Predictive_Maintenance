from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence, Self

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.ml.base_model import BaseMaintenanceModel, FeatureInput, PredictionOutput
from app.ml.features import DEFAULT_FEATURE_COLUMNS, feature_dict_to_ordered_list


class IsolationForestMaintenanceModel(BaseMaintenanceModel):
    """First working anomaly-detection model for predictive maintenance.

    This model detects abnormal sensor behavior. It is intentionally wrapped
    behind BaseMaintenanceModel so it can later be replaced by XGBoost,
    Autoencoder, or LSTM RUL models without changing API routes or frontend
    contracts.
    """

    model_type = "isolation_forest"

    def __init__(
        self,
        model: IsolationForest,
        scaler: StandardScaler,
        *,
        version: str = "1.0.0",
        feature_columns: Sequence[str] | None = None,
    ) -> None:
        self.model = model
        self.scaler = scaler
        self.version = version
        self.feature_columns = list(feature_columns or DEFAULT_FEATURE_COLUMNS)

    @classmethod
    def train(cls, training_data: Any, **kwargs: Any) -> Self:
        feature_columns = list(kwargs.get("feature_columns") or DEFAULT_FEATURE_COLUMNS)
        matrix = _coerce_training_matrix(training_data, feature_columns)
        if matrix.shape[0] < 2:
            raise ValueError("Isolation Forest training requires at least two rows.")

        scaler = StandardScaler()
        scaled_matrix = scaler.fit_transform(matrix)

        model = IsolationForest(
            contamination=float(kwargs.get("contamination", 0.15)),
            random_state=int(kwargs.get("random_state", 42)),
        )
        model.fit(scaled_matrix)

        return cls(
            model=model,
            scaler=scaler,
            version=str(kwargs.get("version", "1.0.0")),
            feature_columns=feature_columns,
        )

    def predict(self, features: FeatureInput) -> PredictionOutput:
        row = self._feature_input_to_row(features)
        scaled_row = self.scaler.transform(np.asarray([row], dtype=float))
        raw_decision_score = float(self.model.decision_function(scaled_row)[0])
        prediction_label = int(self.model.predict(scaled_row)[0])

        anomaly_score = _decision_score_to_anomaly_score(raw_decision_score)
        risk_level = _risk_level_from_score(anomaly_score)
        confidence = _confidence_from_score(anomaly_score)

        return {
            "anomaly_score": anomaly_score,
            "is_anomaly": prediction_label == -1 or anomaly_score >= 0.6,
            "risk_level": risk_level,
            "confidence": confidence,
            "model_type": self.model_type,
            "model_version": self.version,
        }

    def save(self, path: str | Path, scaler_path: str | Path | None = None) -> None:
        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, model_path)

        if scaler_path is None:
            scaler_path = model_path.with_name("scaler_v1.joblib")
        scaler_output_path = Path(scaler_path)
        scaler_output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.scaler, scaler_output_path)

    @classmethod
    def load(
        cls,
        path: str | Path,
        scaler_path: str | Path | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        model_path = Path(path)
        if scaler_path is None:
            scaler_path = model_path.with_name("scaler_v1.joblib")

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        metadata = metadata or {}

        return cls(
            model=model,
            scaler=scaler,
            version=str(metadata.get("version", "1.0.0")),
            feature_columns=metadata.get("features") or DEFAULT_FEATURE_COLUMNS,
        )

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_type": self.model_type,
            "model_version": self.version,
            "features": self.feature_columns,
            "target_type": "anomaly_detection",
        }

    def _feature_input_to_row(self, features: FeatureInput) -> list[float]:
        if isinstance(features, Mapping):
            return feature_dict_to_ordered_list(features, self.feature_columns)
        return [float(value) for value in features]


def _coerce_training_matrix(training_data: Any, feature_columns: Sequence[str]) -> np.ndarray:
    if isinstance(training_data, pd.DataFrame):
        missing = [column for column in feature_columns if column not in training_data.columns]
        if missing:
            raise ValueError(f"Training data is missing feature column(s): {', '.join(missing)}")
        return training_data.loc[:, feature_columns].astype(float).to_numpy()

    if isinstance(training_data, list) and training_data and isinstance(training_data[0], Mapping):
        rows = [feature_dict_to_ordered_list(row, feature_columns) for row in training_data]
        return np.asarray(rows, dtype=float)

    return np.asarray(training_data, dtype=float)


def _decision_score_to_anomaly_score(decision_score: float) -> float:
    # IsolationForest decision scores are higher for normal points. This MVP
    # maps them into a bounded anomaly score; later models can provide calibrated
    # probabilities without changing the frontend response contract.
    score = 0.5 - decision_score
    return round(float(np.clip(score, 0.0, 1.0)), 4)


def _risk_level_from_score(anomaly_score: float) -> str:
    if anomaly_score >= 0.85:
        return "critical"
    if anomaly_score >= 0.65:
        return "high"
    if anomaly_score >= 0.4:
        return "medium"
    return "low"


def _confidence_from_score(anomaly_score: float) -> str:
    if anomaly_score >= 0.8 or anomaly_score <= 0.2:
        return "high"
    if anomaly_score >= 0.6 or anomaly_score <= 0.35:
        return "medium"
    return "low"
