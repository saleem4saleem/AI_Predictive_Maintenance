from __future__ import annotations

from datetime import date, timedelta

from app.contracts.prediction_contract import PredictionResponse
from app.ml.predict import predict_with_active_model
from app.services.asset_service import get_asset
from app.services.feature_service import calculate_sensor_severity


def run_model_prediction(features: dict[str, float]) -> dict:
    prediction = predict_with_active_model(features)
    if prediction.get("risk_level") == "unknown":
        severity = calculate_sensor_severity(features)
        prediction.update(
            {
                "anomaly_score": severity,
                "is_anomaly": severity >= 0.6,
                "risk_level": _risk_level_from_score(severity),
                "confidence": "low",
                "model_type": "heuristic_fallback",
                "model_version": "fallback",
            }
        )
    return prediction


def _risk_level_from_score(score: float) -> str:
    if score >= 0.85:
        return "critical"
    if score >= 0.65:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def get_prediction(asset_id: int | str) -> PredictionResponse:
    """Return a stable prediction contract using placeholder service data.

    A later phase can replace this body with prediction_orchestrator.run_prediction
    without changing routes or frontend response fields.
    """

    asset = get_asset(asset_id)
    today = date.today()
    profile = _placeholder_risk_profile(asset.risk_level)
    predicted_date = today + timedelta(days=profile["rul_days"]) if asset.risk_level != "low" else None

    return PredictionResponse(
        asset_id=int(asset.asset_id),
        asset_code=asset.asset_code,
        asset_name=asset.asset_name,
        health_score=asset.health_score,
        condition=asset.status,
        failure_probability_7_days=profile["probability_7_days"],
        failure_probability_30_days=profile["probability_30_days"],
        predicted_failure_date=predicted_date.isoformat() if predicted_date else None,
        remaining_useful_life_days=profile["rul_days"],
        predicted_failure_mode=_placeholder_failure_mode(asset.asset_name, asset.risk_level),
        risk_level=asset.risk_level,
        confidence="medium",
        recommended_action=_placeholder_action(asset.asset_name, asset.risk_level),
        explanation="This is a placeholder prediction until the ML model is connected.",
        model_version="not_connected_yet",
    )


def run_prediction(asset_id: int | str) -> PredictionResponse:
    return get_prediction(asset_id)


def _placeholder_risk_profile(risk_level: str) -> dict[str, float | int]:
    profiles = {
        "low": {"probability_7_days": 0.05, "probability_30_days": 0.12, "rul_days": 120},
        "medium": {"probability_7_days": 0.18, "probability_30_days": 0.42, "rul_days": 45},
        "high": {"probability_7_days": 0.36, "probability_30_days": 0.68, "rul_days": 18},
        "critical": {"probability_7_days": 0.72, "probability_30_days": 0.91, "rul_days": 5},
    }
    return profiles.get(risk_level, profiles["low"])


def _placeholder_failure_mode(asset_name: str, risk_level: str) -> str | None:
    if risk_level == "low":
        return None
    mapping = {
        "IS Forming Machine": "forming section pneumatic or mechanical wear",
        "Inspection Machine": "vision/rejection equipment instability",
        "Packaging Machine": "wear in sealing, labeling, or suction system",
        "Conveyor System": "belt alignment or transport drive issue",
    }
    return mapping.get(asset_name, "condition trend requires technician validation")


def _placeholder_action(asset_name: str, risk_level: str) -> str:
    if risk_level == "low":
        return "Continue normal monitoring"
    if asset_name == "IS Forming Machine":
        return "Inspect forming section wear points, lubrication, and pneumatic response"
    if asset_name == "Packaging Machine":
        return "Inspect suction cups, sealing temperature, labels, and transport timing"
    if asset_name == "Inspection Machine":
        return "Check camera cleanliness, reject timing, and scanner calibration"
    return f"Inspect {asset_name} during the next planned maintenance window"
