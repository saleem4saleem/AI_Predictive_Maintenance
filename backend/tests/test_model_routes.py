from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_active_model_route_returns_safe_public_status() -> None:
    response = client.get("/api/v1/models/active")

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_type"] == "isolation_forest"
    assert payload["version"] == "1.0.0"
    assert payload["status"] in {"not_trained", "trained"}
    assert "features" in payload
    assert "model_path" not in payload
    assert "scaler_path" not in payload
