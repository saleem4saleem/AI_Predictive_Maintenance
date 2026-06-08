from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_maintenance_plan_endpoint_returns_stable_contract() -> None:
    response = client.get("/api/v1/maintenance-plans/6")

    assert response.status_code == 200
    payload = response.json()
    required_fields = {
        "asset_id",
        "next_planned_maintenance",
        "ai_recommended_maintenance",
        "recommendation",
        "priority",
        "reason",
        "planned_vs_predicted_status",
    }

    assert required_fields.issubset(payload)
    assert payload["asset_id"] == 6
    assert payload["recommendation"] in {
        "keep planned maintenance",
        "move maintenance earlier",
        "urgent inspection needed",
        "monitor only",
    }
    assert payload["priority"] in {"low", "medium", "high", "critical"}
    assert payload["reason"]
    assert payload["planned_vs_predicted_status"]


def test_maintenance_plan_endpoint_returns_404_for_missing_asset() -> None:
    response = client.get("/api/v1/maintenance-plans/999999")

    assert response.status_code == 404
