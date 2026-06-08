from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_core_api_structure_endpoints_are_available() -> None:
    endpoints = [
        "/api/v1/health",
        "/api/v1/health/database",
        "/api/v1/health/model",
        "/api/v1/models/active",
        "/api/v1/maintenance-plans/1",
        "/api/v1/recommendations/1",
        "/api/v1/sensors/1",
        "/api/v1/sensors/1/history",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, endpoint


def test_active_model_endpoint_returns_stable_contract() -> None:
    response = client.get("/api/v1/models/active")

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_type"] in {"not_connected_yet", "isolation_forest"}
    assert payload["status"] in {"not_connected_yet", "not_trained", "trained", "metadata_only", "healthy", "degraded", "unavailable"}
    assert "features" in payload
