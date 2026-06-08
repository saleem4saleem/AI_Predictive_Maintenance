from fastapi.testclient import TestClient

from app.contracts.prediction_contract import PredictionResponse
from app.main import app


client = TestClient(app)


def test_prediction_endpoint_contract_is_stable() -> None:
    response = client.get("/api/v1/predictions/6")
    assert response.status_code == 200
    data = response.json()
    for field in [
        "asset_id",
        "asset_code",
        "asset_name",
        "health_score",
        "condition",
        "failure_probability_7_days",
        "failure_probability_30_days",
        "predicted_failure_date",
        "remaining_useful_life_days",
        "predicted_failure_mode",
        "risk_level",
        "confidence",
        "recommended_action",
        "explanation",
        "model_version",
    ]:
        assert field in data
    assert data["asset_code"] == "PACKAGING_001"


def test_prediction_response_can_be_created_with_required_fields() -> None:
    response = PredictionResponse(
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
        explanation="This is a stable contract test.",
        model_version="not_connected_yet",
    )

    assert response.asset_id == 1
    assert response.model_version == "not_connected_yet"
