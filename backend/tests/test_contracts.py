from app.contracts.asset_contract import AssetBasicResponse
from app.contracts.asset_detail_contract import (
    AIExplanationContract,
    AssetDetailResponse,
    CurrentConditionContract,
    FeedbackStatusContract,
    RecommendedActionContract,
    SensorSummaryContract as AssetDetailSensorSummary,
)
from app.contracts.feedback_contract import FeedbackRequest, FeedbackResponse
from app.contracts.maintenance_plan_contract import MaintenancePlanResponse
from app.contracts.model_contract import ActiveModelResponse
from app.contracts.overview_contract import AssetOverviewCard, OverviewResponse, ProductionFlowAsset
from app.contracts.prediction_contract import PredictionResponse
from app.contracts.rag_contract import RagSearchRequest, RagSearchResponse, RagSearchResult
from app.contracts.recommendation_contract import RecommendationItem, RecommendationResponse
from app.contracts.sensor_contract import SensorHistoryPoint, SensorHistoryResponse, SensorLatestResponse


def test_feedback_request_accepts_optional_fields() -> None:
    feedback = FeedbackRequest(asset_id=1)

    assert feedback.asset_id == 1
    assert feedback.prediction_id is None
    assert feedback.was_prediction_correct is None


def test_active_model_response_contract_is_frontend_friendly() -> None:
    response = ActiveModelResponse(
        model_type="not_connected_yet",
        version="not_connected_yet",
        status="not_connected_yet",
        trained_at=None,
        features=["vibration", "temperature"],
    )

    assert response.model_type == "not_connected_yet"
    assert response.features == ["vibration", "temperature"]


def test_sensor_contracts_can_represent_latest_and_history() -> None:
    latest = SensorLatestResponse(asset_id=1, timestamp=None, vibration=2.1)
    history = SensorHistoryResponse(
        asset_id=1,
        history=[
            SensorHistoryPoint(
                timestamp="2026-05-18T10:00:00Z",
                vibration=2.1,
                temperature=75.0,
            )
        ],
    )

    assert latest.asset_id == 1
    assert history.history[0].timestamp == "2026-05-18T10:00:00Z"


def test_rag_contracts_are_stable() -> None:
    request = RagSearchRequest(query="bearing failure", asset_id=1)
    response = RagSearchResponse(
        query=request.query,
        results=[
            RagSearchResult(
                source_type="work_order",
                title="Bearing replacement",
                summary="Repeated high vibration before replacement.",
                score=0.8,
            )
        ],
    )

    assert response.query == "bearing failure"
    assert response.results[0].source_type == "work_order"


def test_frontend_response_contracts_can_be_instantiated() -> None:
    asset = AssetBasicResponse(
        asset_id=1,
        asset_code="FURNACE_001",
        asset_name="Furnace",
        asset_type="Thermal Process",
        location="Hot End",
        status="healthy",
        criticality="critical",
        health_score=91,
        risk_level="low",
    )
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
        explanation="Stable contract.",
        model_version="not_connected_yet",
    )
    maintenance_plan = MaintenancePlanResponse(
        asset_id=1,
        next_planned_maintenance="2026-06-15",
        ai_recommended_maintenance=None,
        recommendation="keep planned maintenance",
        priority="low",
        reason="Plan is acceptable.",
        planned_vs_predicted_status="planned_before_predicted",
    )
    recommendation = RecommendationItem(
        action="Continue monitoring",
        priority="low",
        reason="Healthy asset.",
        due_date=None,
        source="test",
    )

    overview = OverviewResponse(
        factory_name="Demo Glass Factory",
        factory_health=82,
        critical_assets=2,
        open_actions=7,
        weekly_downtime_risk_hours=4.5,
        production_flow=[
            ProductionFlowAsset(
                asset_id=1,
                asset_code="FURNACE_001",
                asset_name="Furnace",
                status="healthy",
                health_score=91,
                risk_level="low",
                predicted_failure_date=None,
                next_planned_maintenance="2026-06-15",
                ai_recommended_maintenance=None,
            )
        ],
        assets=[
            AssetOverviewCard(
                asset_id=1,
                asset_code="FURNACE_001",
                asset_name="Furnace",
                asset_type="Thermal Process",
                status="healthy",
                health_score=91,
                risk_level="low",
                criticality="critical",
                open_actions=0,
                predicted_failure_date=None,
            )
        ],
    )
    detail = AssetDetailResponse(
        asset=asset,
        current_condition=CurrentConditionContract(health_score=91, condition="healthy"),
        sensor_summary=AssetDetailSensorSummary(timestamp=None),
        prediction=prediction,
        maintenance_plan=maintenance_plan,
        recommended_actions=[
            RecommendedActionContract(
                action=recommendation.action,
                priority=recommendation.priority,
                reason=recommendation.reason,
                due_date=recommendation.due_date,
                source=recommendation.source,
            )
        ],
        similar_failures=[],
        ai_explanation=AIExplanationContract(summary="Stable explanation.", confidence="low", fallback_used=True),
        feedback_status=FeedbackStatusContract(feedback_required=False, last_feedback_at=None),
    )

    assert overview.production_flow[0].asset_code == "FURNACE_001"
    assert detail.prediction.asset_id == 1
    assert RecommendationResponse(asset_id=1, recommendations=[recommendation]).recommendations
    assert FeedbackResponse(status="accepted", message="Feedback received successfully", asset_id=1).status == "accepted"
