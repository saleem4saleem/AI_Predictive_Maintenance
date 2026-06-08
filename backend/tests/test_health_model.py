from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_model_route_returns_registry_status_without_paths() -> None:
    response = client.get("/api/v1/health/model")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["model_type"] == "isolation_forest"
    assert payload["version"] == "1.0.0"
    assert payload["status"] in {"not_trained", "trained"}
    assert "model_file_exists" in payload
    assert "scaler_file_exists" in payload
    assert "model_path" not in payload
    assert "scaler_path" not in payload
