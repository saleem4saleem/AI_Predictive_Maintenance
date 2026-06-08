from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.contracts.asset_contract import AssetBasicResponse, AssetContract
from app.contracts.asset_detail_contract import (
    AIExplanationContract,
    AssetDetailResponse,
    CurrentConditionContract,
    FeedbackStatusContract,
    RecommendedActionContract,
    SensorSummaryContract,
    SimilarFailureContract,
)
from app.contracts.feedback_contract import FeedbackCreateContract, FeedbackResponseContract
from app.contracts.maintenance_plan_contract import MaintenancePlanContract
from app.contracts.model_contract import ActiveModelContract
from app.contracts.prediction_contract import PredictionContract
from app.contracts.rag_contract import RagResultContract, RagSearchResponseContract
from app.contracts.recommendation_contract import RecommendationActionContract, RecommendationContract
from app.contracts.sensor_contract import SensorHistoryPoint, SensorHistoryResponse, SensorLatestResponse
from app.services.asset_service import get_asset
from app.services.feedback_service import submit_feedback
from app.services.sensor_service import get_sensor_history_rows


def list_asset_basic_placeholders() -> list[AssetBasicResponse]:
    from app.services.asset_service import list_assets

    return [_asset_basic_response(asset) for asset in list_assets()]


def get_asset_basic_placeholder(asset_id: str | int) -> AssetBasicResponse:
    return _asset_basic_response(get_asset(asset_id))


def get_prediction_placeholder(asset_id: str) -> PredictionContract:
    asset = get_asset(asset_id)
    today = date.today()
    profile = _risk_profile(asset.risk_level)
    predicted_date = today + timedelta(days=profile["rul_days"]) if asset.risk_level != "low" else None

    return PredictionContract(
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


def get_maintenance_plan_placeholder(asset_id: str) -> MaintenancePlanContract:
    asset = get_asset(asset_id)
    today = date.today()
    interval = 14 if asset.criticality >= 95 else 21 if asset.criticality >= 85 else 30
    planned_date = today + timedelta(days=interval)
    ai_date = today + timedelta(days=10) if asset.risk_level == "high" else today + timedelta(days=21) if asset.risk_level == "medium" else None
    recommendation = "move maintenance earlier" if ai_date and ai_date < planned_date else "keep planned maintenance"
    reason = "AI placeholder risk date is earlier than the current PM plan." if recommendation == "move maintenance earlier" else "Current PM date is acceptable for the placeholder risk level."

    return MaintenancePlanContract(
        asset_id=int(asset.asset_id),
        next_planned_maintenance=planned_date.isoformat(),
        ai_recommended_maintenance=ai_date.isoformat() if ai_date else None,
        recommendation=recommendation,
        priority="high" if recommendation == "move maintenance earlier" else "normal",
        reason=reason,
        planned_vs_predicted_status=recommendation,
        next_planned_maintenance_date=planned_date.isoformat(),
        preventive_interval_days=interval,
        open_work_orders=1 if asset.status in {"attention", "warning", "critical"} else 0,
        ai_recommended_date=ai_date.isoformat() if ai_date else None,
        planning_status=recommendation,
        timing_advice=reason,
    )


def get_recommendations_placeholder(asset_id: str) -> RecommendationContract:
    asset = get_asset(asset_id)
    action = _placeholder_action(asset.asset_name, asset.risk_level)
    priority = "high" if asset.risk_level in {"high", "critical"} else asset.risk_level
    due_date = str(date.today() + timedelta(days=3 if priority == "high" else 14))
    recommendations = [
        RecommendationActionContract(
            action=action,
            priority=priority,
            reason=f"{asset.asset_name} is currently marked as {asset.status} with {asset.risk_level} risk.",
            due_date=due_date,
            source="api_placeholder",
        )
    ]
    if asset.status == "attention":
        recommendations.append(
            RecommendationActionContract(
                action="Review latest sensor trend and open maintenance actions",
                priority="medium",
                reason="Attention state should be validated before the next production window.",
                due_date=str(date.today() + timedelta(days=7)),
                source="api_placeholder",
            )
        )

    return RecommendationContract(
        asset_id=int(asset.asset_id),
        recommendations=recommendations,
        actions=[item.action for item in recommendations],
        priority=priority,
        reason=recommendations[0].reason,
    )


def get_asset_detail_placeholder(asset_id: str) -> AssetDetailResponse:
    asset = get_asset(asset_id)
    prediction = get_prediction_placeholder(asset.asset_id)
    plan = get_maintenance_plan_placeholder(asset.asset_id)
    recommendation = get_recommendations_placeholder(asset.asset_id)
    similar_failures = get_rag_search_placeholder(f"{asset.asset_name} maintenance issue", asset.asset_id, limit=3).results
    sensor_values = get_latest_sensor_placeholder(asset.asset_id)

    return AssetDetailResponse(
        asset=_asset_basic_response(asset),
        current_condition=CurrentConditionContract(
            health_score=prediction.health_score,
            condition=prediction.condition,
            trend="stable" if prediction.risk_level == "low" else "needs_attention",
            last_updated=sensor_values.timestamp,
        ),
        sensor_summary=SensorSummaryContract(
            timestamp=sensor_values.timestamp,
            vibration=sensor_values.vibration,
            temperature=sensor_values.temperature,
            pressure=sensor_values.pressure,
            current_value=sensor_values.current_value,
            speed=sensor_values.speed,
            flow=sensor_values.flow,
        ),
        prediction=prediction,
        maintenance_plan=plan,
        recommended_actions=[
            RecommendedActionContract(
                action=item.action,
                priority=item.priority,
                reason=item.reason,
                due_date=item.due_date,
                source=item.source,
            )
            for item in recommendation.recommendations
        ],
        similar_failures=[
            SimilarFailureContract(
                source_type=item.source_type,
                title=item.title,
                summary=item.summary,
                score=item.score,
            )
            for item in similar_failures
        ],
        ai_explanation=AIExplanationContract(
            summary=prediction.explanation,
            confidence=prediction.confidence,
            fallback_used=True,
        ),
        feedback_status=FeedbackStatusContract(
            feedback_required=prediction.risk_level in {"medium", "high", "critical"},
            last_feedback_at=None,
        ),
    )


def get_latest_sensor_placeholder(asset_id: str) -> SensorLatestResponse:
    asset = get_asset(asset_id)
    history = get_sensor_history_rows(asset.asset_id, limit=1)
    if not history:
        return SensorLatestResponse(asset_id=int(asset.asset_id), timestamp=None)

    latest = history[-1]
    return SensorLatestResponse(
        asset_id=int(asset.asset_id),
        timestamp=latest.get("timestamp"),
        vibration=float(latest["vibration"]),
        temperature=float(latest["temperature"]),
        pressure=float(latest["pressure"]),
        current_value=float(latest["current_value"]),
        speed=float(latest["speed"]),
        flow=float(latest["flow"]),
    )


def get_sensor_history_placeholder(asset_id: str, limit: int = 24) -> SensorHistoryResponse:
    asset = get_asset(asset_id)
    rows = get_sensor_history_rows(asset.asset_id, limit=limit)
    return SensorHistoryResponse(
        asset_id=int(asset.asset_id),
        history=[
            SensorHistoryPoint(
                timestamp=str(row.get("timestamp")),
                vibration=float(row["vibration"]),
                temperature=float(row["temperature"]),
                pressure=float(row["pressure"]),
                current_value=float(row["current_value"]),
                speed=float(row["speed"]),
                flow=float(row["flow"]),
            )
            for row in rows
        ],
    )


def get_rag_search_placeholder(query: str, asset_id: str | int | None = None, limit: int = 5) -> RagSearchResponseContract:
    asset_name = get_asset(asset_id).asset_name if asset_id else "selected production asset"
    results = [
        RagResultContract(
            source_type="placeholder_case",
            title=f"Similar maintenance case for {asset_name}",
            summary="Historical failure search is not connected yet. This placeholder keeps the API contract stable for future RAG integration.",
            score=0.74,
        )
    ]
    return RagSearchResponseContract(query=query, results=results[:limit])


def accept_feedback_placeholder(feedback: FeedbackCreateContract) -> FeedbackResponseContract:
    response = submit_feedback(feedback)
    response.message = "Feedback received successfully"
    return response


def get_active_model_placeholder() -> ActiveModelContract:
    return ActiveModelContract(
        component="model",
        ok=True,
        status="not_connected_yet",
        detail="The API contract is ready; the active ML model registry will be connected in a later phase.",
        model_type="not_connected_yet",
        version="not_connected_yet",
        model_version="not_connected_yet",
        trained_at="not_connected_yet",
        features=[
            "vibration",
            "temperature",
            "pressure",
            "current_value",
            "speed",
            "flow",
        ],
        target_type="anomaly_detection",
        metrics={},
    )


def _asset_basic_response(asset: AssetContract) -> AssetBasicResponse:
    return AssetBasicResponse(
        asset_id=int(asset.asset_id),
        asset_code=asset.asset_code,
        asset_name=asset.asset_name,
        asset_type=asset.asset_type,
        location=asset.location,
        status=asset.status,
        criticality=_criticality_label(asset.criticality),
        health_score=asset.health_score,
        risk_level=asset.risk_level,
    )


def _criticality_label(value: int) -> str:
    if value >= 95:
        return "critical"
    if value >= 85:
        return "high"
    if value >= 70:
        return "medium"
    return "low"


def _risk_profile(risk_level: str) -> dict[str, Any]:
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
