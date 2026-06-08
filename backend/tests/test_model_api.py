from __future__ import annotations


def test_active_model_api_returns_safe_public_contract(client) -> None:
    response = client.get("/api/v1/models/active")

    assert response.status_code == 200
    payload = response.json()
    for field in ["model_type", "version", "status", "trained_at", "features"]:
        assert field in payload
    assert isinstance(payload["features"], list)
    assert "model_path" not in payload
    assert "scaler_path" not in payload


def test_active_model_api_tolerates_missing_artifacts(client) -> None:
    response = client.get("/api/v1/models/active")

    assert response.status_code == 200
    payload = response.json()
    assert "model_file_exists" in payload
    assert "scaler_file_exists" in payload
    assert isinstance(payload["model_file_exists"], bool)
    assert isinstance(payload["scaler_file_exists"], bool)
