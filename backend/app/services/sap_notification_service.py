from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.services.sap_portal_automation_service import prepare_notification_creation


SAP_DISABLED_MESSAGE = (
    "SAP integration is disabled. Local test notifications are available."
)
SAP_SEND_DISABLED_MESSAGE = (
    "SAP integration is disabled. Notification was not sent to SAP."
)
SAP_PORTAL_UNREACHABLE_MESSAGE = (
    "SAP portal is not reachable from this machine. Use an authorized company "
    "PC/network/VPN/Zscaler session."
)
LOCAL_NOTIFICATION_STATUSES = {"local_test", "ready_for_sap"}


def is_sap_configured() -> bool:
    settings = get_settings()
    portal_url = _portal_url(settings)
    return bool(
        settings.sap_integration_enabled
        and portal_url
        and settings.sap_username
        and settings.sap_password
    )


def is_sap_enabled() -> bool:
    return bool(get_settings().sap_integration_enabled)


def check_sap_portal_reachable() -> dict[str, Any]:
    """Check portal reachability without authenticating or sending credentials."""

    settings = get_settings()
    portal_url = _portal_url(settings)
    if not settings.sap_integration_enabled:
        return {
            "reachable": False,
            "status": "disabled",
            "message": SAP_DISABLED_MESSAGE,
        }
    if not portal_url:
        return {
            "reachable": False,
            "status": "not_configured",
            "message": "SAP portal URL is not configured.",
        }

    request = Request(
        portal_url,
        headers={"User-Agent": "PredictiveMaintenance-SAP-Connectivity-Check/1.0"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=5) as response:
            status_code = getattr(response, "status", 200)
        return {
            "reachable": True,
            "status": "reachable",
            "message": f"SAP portal responded with HTTP {status_code}.",
        }
    except HTTPError as exc:
        return {
            "reachable": True,
            "status": "reachable",
            "message": f"SAP portal responded with HTTP {exc.code}; authentication may be required.",
        }
    except (URLError, TimeoutError, OSError):
        return {
            "reachable": False,
            "status": "sap_portal_unreachable",
            "message": SAP_PORTAL_UNREACHABLE_MESSAGE,
        }


def get_sap_integration_status() -> dict[str, Any]:
    settings = get_settings()
    enabled = bool(settings.sap_integration_enabled)
    portal_url = _portal_url(settings)
    configured = is_sap_configured()

    if not enabled:
        return {
            "enabled": False,
            "configured": False,
            "portal_url": portal_url,
            "reachable": False,
            "status": "disabled",
            "message": SAP_DISABLED_MESSAGE,
        }
    if not portal_url:
        return {
            "enabled": True,
            "configured": False,
            "portal_url": None,
            "reachable": False,
            "status": "not_configured",
            "message": "SAP_PORTAL_URL is not configured.",
        }

    reachability = check_sap_portal_reachable()
    if not reachability["reachable"]:
        return {
            "enabled": True,
            "configured": configured,
            "portal_url": portal_url,
            **reachability,
        }

    if not settings.sap_username or not settings.sap_password:
        return {
            "enabled": True,
            "configured": False,
            "portal_url": portal_url,
            "reachable": True,
            "status": "sap_login_required",
            "message": "SAP portal is reachable, but backend credentials are not configured.",
        }

    return {
        "enabled": True,
        "configured": True,
        "portal_url": portal_url,
        "reachable": True,
        "status": "ready",
        "message": (
            "SAP portal is reachable and credentials are configured. Manual-assisted "
            "notification preparation is available."
        ),
    }


def send_notification_to_sap(notification: dict[str, Any]) -> dict[str, Any]:
    """Prepare a notification for SAP without claiming unverified creation."""

    status = get_sap_integration_status()
    if status["status"] == "disabled":
        current_status = str(notification.get("status") or "local_test")
        preserved_status = (
            current_status
            if current_status in LOCAL_NOTIFICATION_STATUSES
            else "local_test"
        )
        return {
            "status": preserved_status,
            "message": SAP_SEND_DISABLED_MESSAGE,
            "sap_notification_number": None,
            "portal_url": status.get("portal_url"),
        }
    if status["status"] == "not_configured":
        return {
            "status": "sap_failed",
            "message": "SAP integration is not configured. Add SAP settings to local .env.",
            "sap_notification_number": None,
            "portal_url": status.get("portal_url"),
        }
    if status["status"] == "sap_portal_unreachable":
        return {
            "status": "sap_portal_unreachable",
            "message": status["message"],
            "sap_notification_number": None,
            "portal_url": status.get("portal_url"),
        }
    if status["status"] == "sap_login_required":
        return {
            "status": "sap_login_required",
            "message": status["message"],
            "sap_notification_number": None,
            "portal_url": status.get("portal_url"),
        }

    prepared = prepare_notification_creation(notification)
    return {
        **prepared,
        "sap_notification_number": None,
    }


def _portal_url(settings: Any) -> str | None:
    return getattr(settings, "sap_portal_url", None) or getattr(
        settings,
        "sap_base_url",
        None,
    )
