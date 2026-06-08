from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_assets_api_returns_list_contract() -> None:
    response = client.get("/api/v1/assets")

    assert response.status_code == 200
    assets = response.json()
    assert len(assets) == 8
    for field in [
        "asset_id",
        "asset_code",
        "asset_name",
        "asset_type",
        "status",
        "health_score",
        "risk_level",
        "criticality",
    ]:
        assert field in assets[0]


def test_asset_api_returns_basic_asset_information() -> None:
    response = client.get("/api/v1/assets/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_code"] == "FURNACE_001"
    assert payload["asset_type"] == "Thermal Process"
    assert payload["location"] == "Hot End"


def test_asset_api_returns_clean_404_for_unknown_asset() -> None:
    response = client.get("/api/v1/assets/999999")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "resource_not_found"


def test_asset_detail_api_returns_required_sections() -> None:
    response = client.get("/api/v1/assets/1/detail")

    assert response.status_code == 200
    payload = response.json()
    for field in [
        "asset",
        "current_condition",
        "sensor_summary",
        "prediction",
        "maintenance_plan",
        "recommended_actions",
        "similar_failures",
        "ai_explanation",
        "feedback_status",
    ]:
        assert field in payload

    assert {"health_score", "condition"} <= set(payload["current_condition"])
    assert {"vibration", "temperature", "pressure", "current_value", "speed", "flow"} <= set(payload["sensor_summary"])
    assert {"recommended_action", "risk_level", "explanation"} <= set(payload["prediction"])
    assert {"recommendation", "priority", "reason"} <= set(payload["maintenance_plan"])
    assert {"summary", "confidence", "fallback_used"} <= set(payload["ai_explanation"])
