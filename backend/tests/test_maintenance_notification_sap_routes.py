from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services import maintenance_notification_service as notification_service
from app.services import sap_notification_service


@pytest.fixture()
def notification_file(tmp_path, monkeypatch):
    path = tmp_path / "sample_maintenance_notifications.csv"
    monkeypatch.setattr(notification_service, "NOTIFICATIONS_PATH", path)
    return path


def payload() -> dict:
    return {
        "asset_id": 6,
        "component_id": 605,
        "priority": "high",
        "short_text": "Vacuum suction cups showing repeated wear",
        "description": "Local test SAP-ready notification.",
        "source": "component_history",
    }


def test_sap_status_endpoint_never_exposes_password(client, monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: SimpleNamespace(
            sap_integration_enabled=False,
            sap_portal_url="http://sap.example.test/portal",
            sap_username="private-user",
            sap_password="private-password",
        ),
    )

    response = client.get("/api/v1/maintenance-notifications/sap/status")

    assert response.status_code == 200
    text = response.text
    assert "private-password" not in text
    assert "private-user" not in text
    assert set(response.json()) == {
        "enabled",
        "configured",
        "portal_url",
        "reachable",
        "status",
        "message",
    }


def test_mark_ready_for_sap_updates_status(client, notification_file) -> None:
    created = client.post(
        "/api/v1/maintenance-notifications",
        json=payload(),
    ).json()

    response = client.post(
        f"/api/v1/maintenance-notifications/{created['notification_id']}/mark-ready-for-sap"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ready_for_sap"
    assert response.json()["sap_notification_number"] is None


def test_send_to_sap_when_disabled_does_not_claim_success(
    client,
    notification_file,
    monkeypatch,
) -> None:
    created = client.post(
        "/api/v1/maintenance-notifications",
        json=payload(),
    ).json()
    monkeypatch.setattr(
        sap_notification_service,
        "get_sap_integration_status",
        lambda: {
            "enabled": False,
            "configured": False,
            "portal_url": None,
            "reachable": False,
            "status": "disabled",
            "message": "SAP integration is disabled.",
        },
    )

    response = client.post(
        f"/api/v1/maintenance-notifications/{created['notification_id']}/send-to-sap"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "local_test"
    assert body["sap_notification_number"] is None
    assert body["message"] == (
        "SAP integration is disabled. Notification was not sent to SAP."
    )


def test_send_to_sap_when_disabled_preserves_ready_status(
    client,
    notification_file,
    monkeypatch,
) -> None:
    created = client.post(
        "/api/v1/maintenance-notifications",
        json=payload(),
    ).json()
    client.post(
        f"/api/v1/maintenance-notifications/{created['notification_id']}/mark-ready-for-sap"
    )
    monkeypatch.setattr(
        sap_notification_service,
        "get_sap_integration_status",
        lambda: {
            "enabled": False,
            "configured": False,
            "portal_url": None,
            "reachable": False,
            "status": "disabled",
            "message": "SAP integration is disabled.",
        },
    )

    response = client.post(
        f"/api/v1/maintenance-notifications/{created['notification_id']}/send-to-sap"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready_for_sap"
    assert body["sap_notification_number"] is None


def test_manual_sap_confirmation_records_number(client, notification_file) -> None:
    created = client.post(
        "/api/v1/maintenance-notifications",
        json=payload(),
    ).json()

    response = client.post(
        f"/api/v1/maintenance-notifications/{created['notification_id']}/sap-confirm",
        json={
            "sap_notification_number": "10004567",
            "note": "Created manually in IW21 after review.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "sent_to_sap"
    assert body["sap_notification_number"] == "10004567"
    assert body["sap_confirmation_note"] == "Created manually in IW21 after review."
