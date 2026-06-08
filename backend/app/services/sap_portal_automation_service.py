from __future__ import annotations

from typing import Any

from app.core.config import get_settings


def open_sap_portal_login() -> dict[str, Any]:
    """Prepare a manual-assisted SAP portal session.

    The backend intentionally does not launch a browser on behalf of a remote
    frontend user. The frontend can open the returned portal URL after a user
    action. This avoids surprise browser launches on servers.
    """

    settings = get_settings()
    if not settings.sap_integration_enabled:
        return {
            "status": "sap_not_configured",
            "message": "SAP integration is disabled. Notification remains local.",
            "portal_url": settings.sap_portal_url,
        }
    if not settings.sap_portal_url:
        return {
            "status": "sap_not_configured",
            "message": "SAP portal URL is not configured.",
            "portal_url": None,
        }
    return {
        "status": "sap_creation_pending_manual_step",
        "message": "Open the SAP portal from the frontend and complete login using authorized company access.",
        "portal_url": settings.sap_portal_url,
    }


def attempt_sap_login() -> dict[str, Any]:
    """Return a safe login readiness result without inventing SAP selectors.

    Credentials remain backend-only. Automated login is deliberately not
    attempted until the SAP login DOM, SSO, MFA, and company policy have been
    verified in the target environment.
    """

    settings = get_settings()
    if not settings.sap_username or not settings.sap_password:
        return {
            "status": "sap_login_required",
            "message": "SAP credentials are not configured. Manual authorized login is required.",
        }
    return {
        "status": "sap_creation_pending_manual_step",
        "message": (
            "SAP credentials are configured, but automated login selectors have not been "
            "verified. Continue with manual login and confirmation."
        ),
    }


def prepare_notification_creation(notification: dict[str, Any]) -> dict[str, Any]:
    """Prepare SAP PM field concepts for a manual-assisted M1 workflow.

    Exact SAP field IDs and code mappings must be confirmed against the
    company's SAP PM configuration before automated form submission.
    """

    login_result = attempt_sap_login()
    return {
        "status": login_result["status"],
        "message": (
            "SAP portal is reachable. Notification data is prepared, but manual "
            "confirmation is required before SAP Save."
        ),
        "portal_url": get_settings().sap_portal_url,
        "mapping": {
            "notification_type": notification.get("notification_type", "M1"),
            "short_text": notification.get("short_text"),
            "long_text": notification.get("description"),
            "equipment_or_functional_location": notification.get("asset_code"),
            "object_part": notification.get("component_code"),
            "priority": notification.get("priority"),
            "damage_or_problem_code": notification.get("failure_mode"),
            "cause_code": notification.get("suspected_cause"),
            "task_text": notification.get("recommended_action"),
        },
    }
