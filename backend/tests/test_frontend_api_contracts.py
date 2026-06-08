from __future__ import annotations


def test_frontend_critical_get_endpoints_keep_required_shapes(client) -> None:
    checks = [
        (
            "/api/v1/overview",
            {
                "factory_name",
                "factory_health",
                "critical_assets",
                "open_actions",
                "weekly_downtime_risk_hours",
                "production_flow",
                "assets",
            },
        ),
        (
            "/api/v1/assets/6/detail",
            {
                "asset",
                "current_condition",
                "sensor_summary",
                "prediction",
                "maintenance_plan",
                "recommended_actions",
                "similar_failures",
                "ai_explanation",
                "feedback_status",
            },
        ),
        (
            "/api/v1/predictions/6",
            {
                "asset_id",
                "asset_code",
                "asset_name",
                "health_score",
                "condition",
                "failure_probability_7_days",
                "failure_probability_30_days",
                "predicted_failure_date",
                "remaining_useful_life_days",
                "predicted_failure_mode",
                "risk_level",
                "confidence",
                "recommended_action",
                "explanation",
                "model_version",
            },
        ),
        (
            "/api/v1/maintenance-plans/6",
            {
                "asset_id",
                "next_planned_maintenance",
                "ai_recommended_maintenance",
                "recommendation",
                "priority",
                "reason",
                "planned_vs_predicted_status",
            },
        ),
        (
            "/api/v1/recommendations/6",
            {"asset_id", "recommendations"},
        ),
        (
            "/api/v1/models/active",
            {"model_type", "version", "status", "trained_at", "features"},
        ),
    ]

    for url, fields in checks:
        response = client.get(url)
        assert response.status_code == 200, url
        assert fields <= set(response.json()), url


def test_frontend_critical_post_endpoints_keep_required_shapes(client, tmp_path, monkeypatch) -> None:
    import app.services.feedback_service as feedback_service

    monkeypatch.setattr(feedback_service, "FEEDBACK_PATH", tmp_path / "feedback.csv")

    rag_response = client.post(
        "/api/v1/rag/search",
        json={"query": "high vibration bearing failure", "asset_id": 3},
    )
    feedback_response = client.post(
        "/api/v1/feedback",
        json={
            "asset_id": 6,
            "prediction_id": 101,
            "was_prediction_correct": True,
            "actual_failure_happened": True,
            "actual_failure_mode": "suction cup wear",
            "action_taken": "Replaced suction cups",
            "timing_feedback": "correct",
            "technician_comment": "Prediction was useful.",
        },
    )

    assert rag_response.status_code == 200
    assert {"query", "results"} <= set(rag_response.json())
    assert feedback_response.status_code == 200
    assert {"status", "message", "asset_id"} <= set(feedback_response.json())
