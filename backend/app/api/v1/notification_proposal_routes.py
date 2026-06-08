from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query

from app.contracts.sap_notification_contracts import (
    CreateSAPNotificationRequest,
    NotificationApprovalRequest,
    NotificationProposal,
    NotificationRejectionRequest,
    SAPNotificationFormPayload,
    SAPNotificationResponse,
)
from app.services.notification_proposal_service import (
    approve_proposal,
    create_in_sap,
    get_pending_proposals,
    get_proposal,
    get_proposal_history,
    get_sap_form_payload,
    reject_proposal,
)

router = APIRouter(prefix="/notification-proposals", tags=["notification-proposals"])


@router.get("/pending", response_model=list[NotificationProposal])
async def read_pending_notification_proposals() -> list[NotificationProposal]:
    return get_pending_proposals()


@router.get("/history", response_model=list[NotificationProposal])
async def read_notification_proposal_history(
    status: str | None = Query(default=None),
) -> list[NotificationProposal]:
    return get_proposal_history(status)


@router.get("/{proposal_id}", response_model=NotificationProposal)
async def read_notification_proposal(proposal_id: UUID) -> NotificationProposal:
    return get_proposal(proposal_id)


@router.post("/{proposal_id}/approve", response_model=NotificationProposal)
async def approve_notification_proposal(
    proposal_id: UUID,
    request: NotificationApprovalRequest,
) -> NotificationProposal:
    return approve_proposal(proposal_id, request.reviewer_name, request.comments)


@router.post("/{proposal_id}/reject", response_model=NotificationProposal)
async def reject_notification_proposal(
    proposal_id: UUID,
    request: NotificationRejectionRequest,
) -> NotificationProposal:
    return reject_proposal(proposal_id, request.reviewer_name, request.reason)


@router.get("/{proposal_id}/sap-form-data", response_model=SAPNotificationFormPayload)
async def read_sap_notification_form_data(proposal_id: UUID) -> SAPNotificationFormPayload:
    return get_sap_form_payload(proposal_id)


@router.post("/{proposal_id}/create-in-sap", response_model=SAPNotificationResponse)
async def create_sap_notification(
    proposal_id: UUID,
    request: CreateSAPNotificationRequest,
) -> SAPNotificationResponse:
    return create_in_sap(proposal_id, request.sap_form_data)
