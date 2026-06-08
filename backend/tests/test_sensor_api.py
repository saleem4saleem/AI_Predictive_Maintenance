from __future__ import annotations


SENSOR_FIELDS = {
    "asset_id",
    "timestamp",
    "vibration",
    "temperature",
    "pressure",
    "current_value",
    "speed",
    "flow",
}


def test_latest_sensor_endpoint_returns_frontend_contract(client, sample_asset_id: int) -> None:
    response = client.get(f"/api/v1/sensors/{sample_asset_id}")

    assert response.status_code == 200
    payload = response.json()
    assert SENSOR_FIELDS.issubset(payload)
    assert payload["asset_id"] == sample_asset_id


def test_sensor_history_endpoint_returns_chart_points(client, sample_asset_id: int) -> None:
    response = client.get(f"/api/v1/sensors/{sample_asset_id}/history?limit=3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_id"] == sample_asset_id
    assert isinstance(payload["history"], list)
    assert len(payload["history"]) <= 3
    assert payload["history"]
    assert SENSOR_FIELDS - {"asset_id"} <= set(payload["history"][0])


def test_sensor_endpoint_returns_clean_404_for_missing_asset(client, invalid_asset_id: int) -> None:
    response = client.get(f"/api/v1/sensors/{invalid_asset_id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "resource_not_found"
