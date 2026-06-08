from __future__ import annotations


def test_recommendation_endpoint_returns_action_list(client, attention_asset_id: int) -> None:
    response = client.get(f"/api/v1/recommendations/{attention_asset_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_id"] == attention_asset_id
    assert isinstance(payload["recommendations"], list)
    assert payload["recommendations"]
    first = payload["recommendations"][0]
    assert {"action", "priority", "reason", "due_date", "source"} <= set(first)
    assert first["action"]
    assert first["priority"] in {"low", "medium", "high", "critical"}


def test_recommendation_endpoint_returns_404_for_missing_asset(client, invalid_asset_id: int) -> None:
    response = client.get(f"/api/v1/recommendations/{invalid_asset_id}")

    assert response.status_code == 404
