from __future__ import annotations

import csv
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.contracts.maintenance_notification_contract import (
    MaintenanceNotificationCreateRequest,
    MaintenanceNotificationListResponse,
    MaintenanceNotificationResponse,
)
from app.core.config import PROJECT_ROOT
from app.exceptions import InvalidRequestError, ResourceNotFoundError
from app.services.asset_component_service import get_component_by_id
from app.services.asset_service import get_asset


NOTIFICATIONS_PATH = PROJECT_ROOT / "data" / "sample" / "sample_maintenance_notifications.csv"
LOCAL_TEST_MESSAGE = (
    "Maintenance notification created locally for testing. It has not been sent to SAP yet."
)
CSV_COLUMNS = [
    "notification_id",
    "asset_id",
    "asset_code",
    "asset_name",
    "component_id",
    "component_code",
    "component_name",
    "notification_type",
    "priority",
    "short_text",
    "description",
    "failure_mode",
    "suspected_cause",
    "recommended_action",
    "source",
    "status",
    "sap_notification_number",
    "sap_confirmation_note",
    "created_at",
    "updated_at",
    "requested_by",
    "status_message",
]
ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}
ALLOWED_STATUSES = {
    "local_test",
    "ready_for_sap",
    "sap_login_required",
    "sap_portal_unreachable",
    "sap_creation_pending_manual_step",
    "sap_not_configured",
    "sent_to_sap",
    "sap_failed",
}
_WRITE_LOCK = threading.Lock()


def create_notification(
    payload: MaintenanceNotificationCreateRequest | dict[str, Any],
) -> MaintenanceNotificationResponse:
    request = (
        payload
        if isinstance(payload, MaintenanceNotificationCreateRequest)
        else MaintenanceNotificationCreateRequest(**payload)
    )
    if request.priority not in ALLOWED_PRIORITIES:
        raise InvalidRequestError(
            f"Invalid priority '{request.priority}'. Use low, medium, high, or critical."
        )

    asset = get_asset(request.asset_id)
    component = None
    if request.component_id is not None:
        component = get_component_by_id(request.component_id)
        if component.asset_id != int(asset.asset_id):
            raise InvalidRequestError(
                f"Component '{request.component_id}' does not belong to asset '{request.asset_id}'."
            )

    with _WRITE_LOCK:
        _ensure_storage_file()
        notification_id = generate_local_notification_id()
        created_at = datetime.now(timezone.utc).isoformat()
        row = {
            "notification_id": notification_id,
            "asset_id": int(asset.asset_id),
            "asset_code": request.asset_code or asset.asset_code,
            "asset_name": request.asset_name or asset.asset_name,
            "component_id": component.component_id if component else request.component_id,
            "component_code": (
                component.component_code if component else _clean_optional(request.component_code)
            ),
            "component_name": (
                component.component_name if component else _clean_optional(request.component_name)
            ),
            "notification_type": request.notification_type.strip() or "M1",
            "priority": request.priority,
            "short_text": request.short_text.strip(),
            "description": request.description.strip(),
            "failure_mode": _clean_optional(request.failure_mode),
            "suspected_cause": _clean_optional(request.suspected_cause),
            "recommended_action": _clean_optional(request.recommended_action),
            "source": request.source,
            "status": "local_test",
            "sap_notification_number": None,
            "sap_confirmation_note": None,
            "created_at": created_at,
            "updated_at": created_at,
            "requested_by": _clean_optional(request.requested_by),
            "status_message": LOCAL_TEST_MESSAGE,
        }
        with NOTIFICATIONS_PATH.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
            writer.writerow({column: _serialize(row.get(column)) for column in CSV_COLUMNS})

    return _row_to_response(row)


def list_notifications(asset_id: int | None = None) -> MaintenanceNotificationListResponse:
    _ensure_storage_file()
    notifications = [_row_to_response(row) for row in _read_rows()]
    if asset_id is not None:
        get_asset(asset_id)
        notifications = [
            notification
            for notification in notifications
            if notification.asset_id == int(asset_id)
        ]
    notifications.sort(key=lambda item: item.created_at, reverse=True)
    return MaintenanceNotificationListResponse(
        notifications=notifications,
        total=len(notifications),
    )


def get_notification(notification_id: str) -> MaintenanceNotificationResponse:
    _ensure_storage_file()
    normalized = notification_id.strip().upper()
    for row in _read_rows():
        if str(row.get("notification_id", "")).strip().upper() == normalized:
            return _row_to_response(row)
    raise ResourceNotFoundError(
        f"Maintenance notification '{notification_id}' was not found."
    )


def mark_ready_for_sap(notification_id: str) -> MaintenanceNotificationResponse:
    return update_notification_status(
        notification_id,
        status="ready_for_sap",
        message=(
            "Maintenance notification marked ready for SAP. It has not been sent to SAP yet."
        ),
    )


def update_notification_status(
    notification_id: str,
    *,
    status: str,
    message: str,
    sap_notification_number: str | None = None,
    sap_confirmation_note: str | None = None,
) -> MaintenanceNotificationResponse:
    if status not in ALLOWED_STATUSES:
        raise InvalidRequestError(f"Invalid notification status '{status}'.")

    def updater(row: dict[str, Any]) -> dict[str, Any]:
        row["status"] = status
        row["status_message"] = message
        row["updated_at"] = datetime.now(timezone.utc).isoformat()
        if sap_notification_number is not None:
            row["sap_notification_number"] = sap_notification_number
        if sap_confirmation_note is not None:
            row["sap_confirmation_note"] = sap_confirmation_note
        return row

    return _update_notification(notification_id, updater)


def record_sap_confirmation(
    notification_id: str,
    sap_notification_number: str,
    note: str | None = None,
) -> MaintenanceNotificationResponse:
    if not sap_notification_number.strip():
        raise InvalidRequestError("SAP notification number is required.")

    return update_notification_status(
        notification_id,
        status="sent_to_sap",
        message="SAP notification number recorded manually.",
        sap_notification_number=sap_notification_number.strip(),
        sap_confirmation_note=_clean_optional(note),
    )


def generate_local_notification_id() -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    prefix = f"MN-{today}-"
    sequence_numbers = []
    for row in _read_rows():
        notification_id = str(row.get("notification_id", ""))
        if notification_id.startswith(prefix):
            try:
                sequence_numbers.append(int(notification_id.rsplit("-", 1)[-1]))
            except ValueError:
                continue
    return f"{prefix}{max(sequence_numbers, default=0) + 1:04d}"


def _ensure_storage_file() -> None:
    NOTIFICATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not NOTIFICATIONS_PATH.exists():
        with NOTIFICATIONS_PATH.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        return

    rows = _read_rows_without_ensure()
    existing_columns = list(rows[0].keys()) if rows else _read_header()
    if existing_columns == CSV_COLUMNS:
        return

    normalized_rows = [
        {column: _serialize(row.get(column)) for column in CSV_COLUMNS}
        for row in rows
    ]
    with NOTIFICATIONS_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(normalized_rows)


def _read_rows() -> list[dict[str, str]]:
    _ensure_storage_file()
    return _read_rows_without_ensure()


def _read_rows_without_ensure() -> list[dict[str, str]]:
    if not NOTIFICATIONS_PATH.exists():
        return []
    with NOTIFICATIONS_PATH.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def _read_header() -> list[str]:
    if not NOTIFICATIONS_PATH.exists():
        return []
    with NOTIFICATIONS_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        return next(reader, [])


def _write_rows(rows: list[dict[str, Any]]) -> None:
    with NOTIFICATIONS_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _serialize(row.get(column)) for column in CSV_COLUMNS})


def _update_notification(notification_id: str, updater) -> MaintenanceNotificationResponse:
    _ensure_storage_file()
    normalized = notification_id.strip().upper()
    rows = _read_rows()
    for index, row in enumerate(rows):
        if str(row.get("notification_id", "")).strip().upper() == normalized:
            updated = updater(dict(row))
            rows[index] = updated
            _write_rows(rows)
            return _row_to_response(updated)
    raise ResourceNotFoundError(
        f"Maintenance notification '{notification_id}' was not found."
    )


def _row_to_response(row: dict[str, Any]) -> MaintenanceNotificationResponse:
    status = str(row.get("status") or "local_test")
    message = _clean_optional(row.get("status_message")) or _message_for_status(status)
    return MaintenanceNotificationResponse(
        notification_id=str(row["notification_id"]),
        asset_id=int(row["asset_id"]),
        asset_code=_clean_optional(row.get("asset_code")),
        asset_name=_clean_optional(row.get("asset_name")),
        component_id=_optional_int(row.get("component_id")),
        component_code=_clean_optional(row.get("component_code")),
        component_name=_clean_optional(row.get("component_name")),
        notification_type=str(row.get("notification_type") or "M1"),
        priority=str(row["priority"]),
        short_text=str(row["short_text"]),
        description=str(row["description"]),
        failure_mode=_clean_optional(row.get("failure_mode")),
        suspected_cause=_clean_optional(row.get("suspected_cause")),
        recommended_action=_clean_optional(row.get("recommended_action")),
        source=str(row["source"]),
        status=status,
        sap_notification_number=_clean_optional(row.get("sap_notification_number")),
        sap_confirmation_note=_clean_optional(row.get("sap_confirmation_note")),
        created_at=str(row["created_at"]),
        updated_at=_clean_optional(row.get("updated_at")),
        requested_by=_clean_optional(row.get("requested_by")),
        message=message,
    )


def _clean_optional(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: Any) -> int | None:
    text = _clean_optional(value)
    return None if text is None else int(text)


def _serialize(value: Any) -> str:
    return "" if value is None else str(value)


def _message_for_status(status: str) -> str:
    return {
        "local_test": LOCAL_TEST_MESSAGE,
        "ready_for_sap": "Maintenance notification is ready for SAP review but has not been sent.",
        "sap_login_required": "SAP login or credentials are required before SAP creation can continue.",
        "sap_portal_unreachable": "SAP portal is not reachable from this machine/network.",
        "sap_creation_pending_manual_step": "SAP workflow is prepared, but manual confirmation is required.",
        "sap_not_configured": "SAP integration is disabled or not configured. Notification remains local.",
        "sent_to_sap": "SAP notification number recorded manually.",
        "sap_failed": "SAP send attempt did not complete. Notification remains local.",
    }.get(status, LOCAL_TEST_MESSAGE)
