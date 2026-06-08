from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_backend_health_endpoint() -> None:
    response = client.get("/api/v1/health/backend")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["component"] == "backend"
    assert payload["data"]["status"] == "healthy"


def test_database_health_endpoint_returns_stable_contract() -> None:
    response = client.get("/api/v1/health/database")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["component"] == "database"
    assert "ok" in payload["data"]
    assert "status" in payload["data"]


def test_model_health_endpoint_returns_stable_contract() -> None:
    response = client.get("/api/v1/health/model")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["component"] == "model"
    assert "ok" in payload["data"]
    assert "status" in payload["data"]


def test_overall_health_endpoint_includes_components() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] in {"healthy", "degraded"}
    assert len(payload["data"]["components"]) == 3
