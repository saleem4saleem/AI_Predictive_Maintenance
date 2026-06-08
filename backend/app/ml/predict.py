from __future__ import annotations

from typing import Any

from app.ml.features import FeatureValidationError, validate_feature_dict
from app.ml.model_factory import ModelFactory, ModelFactoryError
from app.ml.model_registry import ModelRegistryError


def predict_with_active_model(features: dict[str, Any]) -> dict[str, Any]:
    """Validate features, load the active backend model, and return prediction data."""
    try:
        validated_features = validate_feature_dict(features)
        model = ModelFactory().load_active_model()
        return model.predict(validated_features)
    except (FeatureValidationError, ModelFactoryError, ModelRegistryError, OSError, FileNotFoundError) as exc:
        return {
            "anomaly_score": None,
            "is_anomaly": False,
            "risk_level": "unknown",
            "confidence": "low",
            "model_type": "unavailable",
            "model_version": "unavailable",
            "error": str(exc),
        }
