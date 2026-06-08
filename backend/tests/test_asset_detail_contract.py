from app.contracts.asset_contract import AssetBasicResponse
from app.contracts.asset_detail_contract import (
    AIExplanationContract,
    AssetDetailResponse,
    CurrentConditionContract,
    FeedbackStatusContract,
    RecommendedActionContract,
    SensorSummaryContract,
    SimilarFailureContract,
)
from app.contracts.maintenance_plan_contract import MaintenancePlanResponse
from app.contracts.prediction_contract import PredictionResponse


def test_asset_detail_response_can_be_created_with_required_sections() -> None:
    prediction = PredictionResponse(
        asset_id=1,
        asset_code="FURNACE_001",
        asset_name="Furnace",
        health_score=91,
        condition="healthy",
        failure_probability_7_days=0.05,
        failure_probability_30_days=0.12,
        predicted_failure_date=None,
        remaining_useful_life_days=120,
        predicted_failure_mode=None,
        risk_level="low",
        confidence="medium",
        recommended_action="Continue normal monitoring",
        explanation="Placeholder explanation.",
        model_version="not_connected_yet",
    )
    detail = AssetDetailResponse(
        asset=AssetBasicResponse(
            asset_id=1,
            asset_code="FURNACE_001",
            asset_name="Furnace",
            asset_type="Thermal Process",
            location="Hot End",
            status="healthy",
            criticality="critical",
        ),
        current_condition=CurrentConditionContract(health_score=91, condition="healthy"),
        sensor_summary=SensorSummaryContract(timestamp=None, vibration=2.0),
        prediction=prediction,
        maintenance_plan=MaintenancePlanResponse(
            asset_id=1,
            next_planned_maintenance="2026-06-15",
            ai_recommended_maintenance=None,
            recommendation="keep planned maintenance",
            priority="normal",
            reason="No early risk detected.",
            planned_vs_predicted_status="keep planned maintenance",
        ),
        recommended_actions=[
            RecommendedActionContract(
                action="Continue normal monitoring",
                priority="low",
            )
        ],
        similar_failures=[
            SimilarFailureContract(
                source_type="placeholder_case",
                title="Similar case",
                summary="No urgent pattern.",
                score=0.5,
            )
        ],
        ai_explanation=AIExplanationContract(summary="Rule-based placeholder.", confidence="medium"),
        feedback_status=FeedbackStatusContract(feedback_required=False),
    )

    assert detail.asset.asset_id == 1
    assert detail.prediction.model_version == "not_connected_yet"
