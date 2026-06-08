from __future__ import annotations

from app.contracts.asset_detail_contract import (
    AIExplanationContract,
    AssetDetailResponse,
    CurrentConditionContract,
    FeedbackStatusContract,
    RecommendedActionContract,
    SensorSummaryContract,
    SimilarFailureContract,
)
from app.services.asset_service import get_asset_by_id
from app.services.asset_component_service import (
    get_asset_maintenance_history,
    get_asset_upcoming_tasks,
    get_components_by_asset,
)
from app.services.llm_service import explain_prediction
from app.services.maintenance_planning_service import get_maintenance_plan
from app.services.prediction_service import get_prediction
from app.services.rag_service import search_knowledge
from app.services.recommendation_service import get_recommendations
from app.services.sensor_service import get_latest_sensor_data


def get_asset_detail(asset_id: int | str) -> AssetDetailResponse:
    """Compose the main asset detail view from smaller backend services."""

    asset = get_asset_by_id(asset_id)
    latest_sensors = get_latest_sensor_data(asset.asset_id)
    prediction = get_prediction(asset.asset_id)
    maintenance_plan = get_maintenance_plan(asset.asset_id)
    recommendations = get_recommendations(asset.asset_id)
    components = get_components_by_asset(asset.asset_id).components
    asset_maintenance_history = get_asset_maintenance_history(asset.asset_id)
    asset_upcoming_tasks = get_asset_upcoming_tasks(asset.asset_id)
    similar_failures = search_knowledge(
        f"{asset.asset_name} {prediction.predicted_failure_mode or 'maintenance'}",
        asset_id=asset.asset_id,
        limit=3,
    )
    ai_explanation = explain_prediction(
        {
            "asset_name": asset.asset_name,
            "health_score": prediction.health_score,
            "risk_level": prediction.risk_level,
            "predicted_failure_date": prediction.predicted_failure_date,
            "remaining_useful_life_days": prediction.remaining_useful_life_days,
            "predicted_failure_mode": prediction.predicted_failure_mode,
            "confidence": prediction.confidence,
            "sensor_summary": {
                "vibration": latest_sensors.vibration,
                "temperature": latest_sensors.temperature,
                "pressure": latest_sensors.pressure,
                "current_value": latest_sensors.current_value,
                "speed": latest_sensors.speed,
                "flow": latest_sensors.flow,
            },
            "recommended_actions": [
                item.action for item in recommendations.recommendations
            ],
            "similar_failures": [item.summary for item in similar_failures.results],
            "maintenance_plan": {
                "next_planned_maintenance": maintenance_plan.next_planned_maintenance,
                "ai_recommended_maintenance": maintenance_plan.ai_recommended_maintenance,
                "recommendation": maintenance_plan.recommendation,
                "priority": maintenance_plan.priority,
            },
        }
    )

    return AssetDetailResponse(
        asset=asset,
        current_condition=CurrentConditionContract(
            health_score=prediction.health_score,
            condition=prediction.condition,
            trend="stable" if prediction.risk_level == "low" else "needs_attention",
            last_updated=latest_sensors.timestamp,
        ),
        sensor_summary=SensorSummaryContract(
            timestamp=latest_sensors.timestamp,
            vibration=latest_sensors.vibration,
            temperature=latest_sensors.temperature,
            pressure=latest_sensors.pressure,
            current_value=latest_sensors.current_value,
            speed=latest_sensors.speed,
            flow=latest_sensors.flow,
        ),
        prediction=prediction,
        maintenance_plan=maintenance_plan,
        recommended_actions=[
            RecommendedActionContract(
                action=item.action,
                priority=item.priority,
                reason=item.reason,
                due_date=item.due_date,
                source=item.source,
            )
            for item in recommendations.recommendations
        ],
        similar_failures=[
            SimilarFailureContract(
                source_type=item.source_type,
                title=item.title,
                summary=item.summary,
                score=item.score,
            )
            for item in similar_failures.results
        ],
        ai_explanation=AIExplanationContract(
            summary=str(ai_explanation["summary"]),
            confidence=str(ai_explanation["confidence"]),
            fallback_used=bool(ai_explanation["fallback_used"]),
        ),
        feedback_status=FeedbackStatusContract(
            feedback_required=prediction.risk_level in {"medium", "high", "critical"},
            last_feedback_at=None,
        ),
        components=components,
        asset_maintenance_history=asset_maintenance_history,
        asset_upcoming_tasks=asset_upcoming_tasks,
    )
