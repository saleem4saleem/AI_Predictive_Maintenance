from app.ml.predict import predict_with_active_model


def test_predict_with_active_model_returns_standard_dictionary() -> None:
    prediction = predict_with_active_model(
        {
            "vibration": 8.5,
            "temperature": 88,
            "pressure": 2.0,
            "current_value": 18,
            "speed": 900,
            "flow": 20,
            "runtime_hours": 1200,
        }
    )

    for field in [
        "anomaly_score",
        "is_anomaly",
        "risk_level",
        "confidence",
        "model_type",
        "model_version",
    ]:
        assert field in prediction


def test_predict_with_active_model_handles_invalid_features_cleanly() -> None:
    prediction = predict_with_active_model({"vibration": "bad"})

    assert prediction["risk_level"] == "unknown"
    assert prediction["model_type"] == "unavailable"
    assert "error" in prediction
