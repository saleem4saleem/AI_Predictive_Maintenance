from __future__ import annotations

import pytest

from app.services import maintenance_notification_service as service


@pytest.fixture()
def notification_file(tmp_path, monkeypatch):
    path = tmp_path / "sample_maintenance_notifications.csv"
    monkeypatch.setattr(service, "NOTIFICATIONS_PATH", path)
    return path


def valid_payload() -> dict:
    return {
        "asset_id": 6,
        "asset_code": "PACKAGING_001",
        "asset_name": "Packaging Machine",
        "component_id": 605,
        "component_code": "PKG-SUCTION",
        "component_name": "Vacuum Suction Cups",
        "priority": "high",
        "short_text": "Vacuum suction cups showing repeated wear",
        "description": "Create local test maintenance notification based on repeated vacuum loss.",
        "failure_mode": "vacuum loss",
        "suspected_cause": "suction cup wear",
        "recommended_action": "Inspect and replace suction cups before next production run",
        "source": "component_history",
        "requested_by": "maintenance_manager",
    }


def test_create_and_read_local_notification(client, notification_file) -> None:
    create_response = client.post(
        "/api/v1/maintenance-notifications",
        json=valid_payload(),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["notification_id"].startswith("MN-")
    assert created["status"] == "local_test"
    assert created["sap_notification_number"] is None

    read_response = client.get(
        f"/api/v1/maintenance-notifications/{created['notification_id']}"
    )
    assert read_response.status_code == 200
    assert read_response.json()["notification_id"] == created["notification_id"]


def test_list_notifications_supports_asset_filter(client, notification_file) -> None:
    client.post("/api/v1/maintenance-notifications", json=valid_payload())

    response = client.get(
        "/api/v1/maintenance-notifications",
        params={"asset_id": 6},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["notifications"][0]["asset_id"] == 6


def test_missing_required_fields_returns_validation_error(client, notification_file) -> None:
    response = client.post(
        "/api/v1/maintenance-notifications",
        json={"asset_id": 6, "priority": "high"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_invalid_priority_returns_clean_validation_error(client, notification_file) -> None:
    payload = valid_payload()
    payload["priority"] = "urgent"

    response = client.post("/api/v1/maintenance-notifications", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
