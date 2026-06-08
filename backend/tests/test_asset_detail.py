from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_asset_detail_endpoint_returns_required_sections() -> None:
    response = client.get("/api/v1/assets/6/detail")
    assert response.status_code == 200
    data = response.json()
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
        assert field in data
    assert data["asset"]["asset_code"] == "PACKAGING_001"
