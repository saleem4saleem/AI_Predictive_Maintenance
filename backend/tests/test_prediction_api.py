from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


REQUIRED_PREDICTION_FIELDS = [
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
]


def test_prediction_get_api_returns_stable_placeholder_contract() -> None:
    response = client.get("/api/v1/predictions/1")

    assert response.status_code == 200
    payload = response.json()
    for field in REQUIRED_PREDICTION_FIELDS:
        assert field in payload
    assert payload["model_version"] == "not_connected_yet"
    assert 0 <= payload["health_score"] <= 100
    assert 0 <= payload["failure_probability_7_days"] <= 1
    assert 0 <= payload["failure_probability_30_days"] <= 1
    assert payload["risk_level"] in {"low", "medium", "high", "critical"}
    assert payload["condition"]
    assert payload["recommended_action"]
    assert payload["explanation"]


def test_prediction_run_api_returns_same_contract() -> None:
    response = client.post("/api/v1/predictions/run", json={"asset_id": "1"})

    assert response.status_code == 200
    payload = response.json()
    for field in REQUIRED_PREDICTION_FIELDS:
        assert field in payload
    assert payload["asset_code"] == "FURNACE_001"
    assert 0 <= payload["health_score"] <= 100
    assert 0 <= payload["failure_probability_7_days"] <= 1
    assert 0 <= payload["failure_probability_30_days"] <= 1
    assert payload["risk_level"] in {"low", "medium", "high", "critical"}


def test_prediction_endpoint_returns_clean_404_for_missing_asset() -> None:
    response = client.get("/api/v1/predictions/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "resource_not_found"
