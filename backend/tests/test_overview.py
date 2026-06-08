from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_overview_endpoint_returns_required_fields() -> None:
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    for field in [
        "factory_name",
        "factory_health",
        "critical_assets",
        "open_actions",
        "weekly_downtime_risk_hours",
        "production_flow",
        "assets",
    ]:
        assert field in data
    assert len(data["assets"]) == 8
