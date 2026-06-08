from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.contracts.maintenance_notification_contract import (
    MaintenanceNotificationCreateRequest,
    MaintenanceNotificationListResponse,
    MaintenanceNotificationResponse,
    SAPIntegrationStatusResponse,
    SAPManualConfirmationRequest,
)
from app.services import maintenance_notification_service
from app.services import sap_notification_service


router = APIRouter(
    prefix="/maintenance-notifications",
    tags=["maintenance-notifications"],
)


@router.post(
    "",
    response_model=MaintenanceNotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_local_maintenance_notification(
    request: MaintenanceNotificationCreateRequest,
) -> MaintenanceNotificationResponse:
    return maintenance_notification_service.create_notification(request)


@router.get("", response_model=MaintenanceNotificationListResponse)
async def read_maintenance_notifications(
    asset_id: int | None = Query(default=None),
) -> MaintenanceNotificationListResponse:
    return maintenance_notification_service.list_notifications(asset_id)


@router.get("/sap/status", response_model=SAPIntegrationStatusResponse)
async def read_sap_integration_status() -> SAPIntegrationStatusResponse:
    return SAPIntegrationStatusResponse(
        **sap_notification_service.get_sap_integration_status()
    )


@router.post(
    "/{notification_id}/mark-ready-for-sap",
    response_model=MaintenanceNotificationResponse,
)
async def mark_notification_ready_for_sap(
    notification_id: str,
) -> MaintenanceNotificationResponse:
    return maintenance_notification_service.mark_ready_for_sap(notification_id)


@router.post(
    "/{notification_id}/send-to-sap",
    response_model=MaintenanceNotificationResponse,
)
async def send_notification_to_sap(
    notification_id: str,
) -> MaintenanceNotificationResponse:
    notification = maintenance_notification_service.get_notification(notification_id)
    result = sap_notification_service.send_notification_to_sap(
        notification.model_dump()
    )
    return maintenance_notification_service.update_notification_status(
        notification_id,
        status=result["status"],
        message=result["message"],
        sap_notification_number=result.get("sap_notification_number"),
    )


@router.post(
    "/{notification_id}/sap-confirm",
    response_model=MaintenanceNotificationResponse,
)
async def confirm_sap_notification_manually(
    notification_id: str,
    request: SAPManualConfirmationRequest,
) -> MaintenanceNotificationResponse:
    return maintenance_notification_service.record_sap_confirmation(
        notification_id,
        request.sap_notification_number,
        request.note,
    )


@router.get("/{notification_id}", response_model=MaintenanceNotificationResponse)
async def read_maintenance_notification(
    notification_id: str,
) -> MaintenanceNotificationResponse:
    return maintenance_notification_service.get_notification(notification_id)
