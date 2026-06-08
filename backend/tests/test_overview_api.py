from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_overview_api_returns_future_dashboard_contract() -> None:
    response = client.get("/api/v1/overview")

    assert response.status_code == 200
    payload = response.json()
    for field in [
        "factory_name",
        "factory_health",
        "critical_assets",
        "open_actions",
        "weekly_downtime_risk_hours",
        "production_flow",
        "assets",
    ]:
        assert field in payload

    assert len(payload["production_flow"]) == 8
    assert isinstance(payload["assets"], list)
    assert payload["assets"]
    first_asset = payload["production_flow"][0]
    for field in [
        "asset_id",
        "asset_code",
        "asset_name",
        "status",
        "health_score",
        "risk_level",
        "predicted_failure_date",
        "next_planned_maintenance",
        "ai_recommended_maintenance",
    ]:
        assert field in first_asset

    first_card = payload["assets"][0]
    for field in [
        "asset_id",
        "asset_code",
        "asset_name",
        "asset_type",
        "status",
        "health_score",
        "risk_level",
        "criticality",
        "open_actions",
        "predicted_failure_date",
    ]:
        assert field in first_card
