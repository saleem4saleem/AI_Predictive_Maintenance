from __future__ import annotations

from app.ml.features import DEFAULT_FEATURE_COLUMNS, validate_feature_dict
from app.services.sensor_service import get_latest_sensor_values


def build_features_for_asset(asset_id: str) -> dict[str, float]:
    values = get_latest_sensor_values(asset_id)
    return validate_feature_dict(values, DEFAULT_FEATURE_COLUMNS)


def calculate_sensor_severity(features: dict[str, float]) -> float:
    severity = 0.0
    severity += min(features["vibration"] / 10, 1.0) * 0.22
    severity += min(max(features["temperature"] - 60, 0) / 1400, 1.0) * 0.12
    severity += min(max(6.5 - features["pressure"], 0) / 3, 1.0) * 0.16
    severity += min(features["current_value"] / 300, 1.0) * 0.14
    severity += min(max(100 - features["speed"], 0) / 40, 1.0) * 0.18
    severity += min(max(80 - features["flow"], 0) / 50, 1.0) * 0.18
    return round(min(severity, 1.0), 4)
