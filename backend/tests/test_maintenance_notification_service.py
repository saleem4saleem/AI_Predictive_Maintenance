from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services import maintenance_notification_service as service
from app.services import sap_notification_service


@pytest.fixture()
def notification_file(tmp_path, monkeypatch):
    path = tmp_path / "sample_maintenance_notifications.csv"
    monkeypatch.setattr(service, "NOTIFICATIONS_PATH", path)
    return path


def sample_payload() -> dict:
    return {
        "asset_id": 6,
        "component_id": 605,
        "priority": "high",
        "short_text": "Vacuum suction cups showing repeated wear",
        "description": "Create local test maintenance notification from component history.",
        "failure_mode": "vacuum loss",
        "suspected_cause": "suction cup wear",
        "recommended_action": "Inspect and replace suction cups before the next production run",
        "source": "component_history",
        "requested_by": "maintenance_manager",
    }


def test_create_notification_returns_local_test(notification_file) -> None:
    notification = service.create_notification(sample_payload())

    assert notification.notification_id.startswith("MN-")
    assert notification.status == "local_test"
    assert notification.sap_notification_number is None
    assert notification.asset_code == "PACKAGING_001"
    assert notification.component_code == "PKG-SUCTION"
    assert "not been sent to SAP" in notification.message


def test_list_and_asset_filter(notification_file) -> None:
    service.create_notification(sample_payload())
    second = sample_payload()
    second.update(
        {
            "asset_id": 3,
            "component_id": 301,
            "short_text": "Mold wear review",
            "source": "ai_recommendation",
        }
    )
    service.create_notification(second)

    all_items = service.list_notifications()
    packaging_items = service.list_notifications(asset_id=6)

    assert all_items.total == 2
    assert packaging_items.total == 1
    assert packaging_items.notifications[0].asset_id == 6


def test_generated_ids_increment(notification_file) -> None:
    first = service.create_notification(sample_payload())
    second = service.create_notification(sample_payload())

    assert first.notification_id != second.notification_id
    assert first.notification_id.endswith("0001")
    assert second.notification_id.endswith("0002")


def test_sap_placeholder_does_not_create_fake_number(monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: SimpleNamespace(
            sap_integration_enabled=False,
            sap_base_url=None,
            sap_username=None,
            sap_password=None,
        ),
    )

    notification = {**sample_payload(), "status": "local_test"}
    result = sap_notification_service.send_notification_to_sap(notification)

    assert result["status"] == "local_test"
    assert result["message"] == (
        "SAP integration is disabled. Notification was not sent to SAP."
    )
    assert result["sap_notification_number"] is None


def test_sap_disabled_preserves_ready_for_sap_status(monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: SimpleNamespace(
            sap_integration_enabled=False,
            sap_base_url=None,
            sap_portal_url=None,
            sap_username=None,
            sap_password=None,
        ),
    )

    result = sap_notification_service.send_notification_to_sap(
        {**sample_payload(), "status": "ready_for_sap"}
    )

    assert result["status"] == "ready_for_sap"
    assert result["sap_notification_number"] is None
