from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


NotificationPriority = Literal["low", "medium", "high", "critical"]
NotificationSource = Literal[
    "manual",
    "ai_recommendation",
    "condition_monitoring",
    "predictive_maintenance",
    "component_history",
]
NotificationStatus = Literal[
    "local_test",
    "ready_for_sap",
    "sap_login_required",
    "sap_portal_unreachable",
    "sap_creation_pending_manual_step",
    "sap_not_configured",
    "sent_to_sap",
    "sap_failed",
]


class MaintenanceNotificationCreateRequest(BaseModel):
    asset_id: int
    asset_code: str | None = None
    asset_name: str | None = None
    component_id: int | None = None
    component_code: str | None = None
    component_name: str | None = None
    notification_type: str = "M1"
    priority: NotificationPriority
    short_text: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    failure_mode: str | None = None
    suspected_cause: str | None = None
    recommended_action: str | None = None
    source: NotificationSource
    requested_by: str | None = None


class MaintenanceNotificationResponse(BaseModel):
    notification_id: str
    asset_id: int
    asset_code: str | None = None
    asset_name: str | None = None
    component_id: int | None = None
    component_code: str | None = None
    component_name: str | None = None
    notification_type: str
    priority: NotificationPriority
    short_text: str
    description: str
    failure_mode: str | None = None
    suspected_cause: str | None = None
    recommended_action: str | None = None
    source: NotificationSource
    status: NotificationStatus
    sap_notification_number: str | None = None
    sap_confirmation_note: str | None = None
    created_at: str
    updated_at: str | None = None
    requested_by: str | None = None
    message: str


class MaintenanceNotificationListResponse(BaseModel):
    notifications: list[MaintenanceNotificationResponse]
    total: int


class SAPIntegrationStatusResponse(BaseModel):
    enabled: bool
    configured: bool
    portal_url: str | None = None
    reachable: bool
    status: str
    message: str


class SAPManualConfirmationRequest(BaseModel):
    sap_notification_number: str = Field(min_length=1, max_length=50)
    note: str | None = None
