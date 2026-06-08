from __future__ import annotations

from types import SimpleNamespace
from urllib.error import URLError

from app.services import sap_notification_service


def settings(**overrides):
    defaults = {
        "sap_integration_enabled": False,
        "sap_portal_url": "http://sap.example.test/portal",
        "sap_username": None,
        "sap_password": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_sap_disabled_returns_safe_status(monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: settings(),
    )

    result = sap_notification_service.get_sap_integration_status()

    assert result["enabled"] is False
    assert result["reachable"] is False
    assert result["status"] == "disabled"
    assert result["message"] == (
        "SAP integration is disabled. Local test notifications are available."
    )


def test_missing_credentials_does_not_crash(monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: settings(sap_integration_enabled=True),
    )
    monkeypatch.setattr(
        sap_notification_service,
        "check_sap_portal_reachable",
        lambda: {
            "reachable": True,
            "status": "reachable",
            "message": "Portal reachable.",
        },
    )

    result = sap_notification_service.get_sap_integration_status()

    assert result["status"] == "sap_login_required"
    assert result["configured"] is False


def test_unreachable_portal_is_safe(monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: settings(
            sap_integration_enabled=True,
            sap_username="configured-user",
            sap_password="configured-password",
        ),
    )
    monkeypatch.setattr(
        sap_notification_service,
        "check_sap_portal_reachable",
        lambda: {
            "reachable": False,
            "status": "sap_portal_unreachable",
            "message": "SAP portal is not reachable.",
        },
    )

    result = sap_notification_service.send_notification_to_sap({})

    assert result["status"] == "sap_portal_unreachable"
    assert result["sap_notification_number"] is None


def test_reachability_error_mentions_authorized_network_options(monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: settings(sap_integration_enabled=True),
    )

    def raise_unreachable(*args, **kwargs):
        raise URLError("blocked")

    monkeypatch.setattr(sap_notification_service, "urlopen", raise_unreachable)

    result = sap_notification_service.check_sap_portal_reachable()

    assert result["status"] == "sap_portal_unreachable"
    assert result["message"] == (
        "SAP portal is not reachable from this machine. Use an authorized company "
        "PC/network/VPN/Zscaler session."
    )


def test_missing_portal_configuration_returns_failed_send(monkeypatch) -> None:
    monkeypatch.setattr(
        sap_notification_service,
        "get_settings",
        lambda: settings(
            sap_integration_enabled=True,
            sap_portal_url=None,
        ),
    )

    result = sap_notification_service.send_notification_to_sap(
        {"status": "ready_for_sap"}
    )

    assert result["status"] == "sap_failed"
    assert result["message"] == (
        "SAP integration is not configured. Add SAP settings to local .env."
    )
    assert result["sap_notification_number"] is None
