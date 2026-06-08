from app.services.model_service import get_active_model


def test_model_service_returns_public_status_without_paths() -> None:
    response = get_active_model()
    payload = response.model_dump()

    assert payload["model_type"] == "isolation_forest"
    assert payload["version"] == "1.0.0"
    assert payload["status"] in {"not_trained", "trained"}
    assert payload["target_type"] == "anomaly_detection"
    assert isinstance(payload["model_file_exists"], bool)
    assert isinstance(payload["scaler_file_exists"], bool)
    assert "model_path" not in payload
    assert "scaler_path" not in payload
