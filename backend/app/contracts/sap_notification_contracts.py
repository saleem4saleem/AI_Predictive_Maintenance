from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


NotificationStatus = str


class NotificationProposal(BaseModel):
    proposal_id: UUID
    asset_id: int
    component_id: int
    asset_code: str
    asset_name: str
    equipment_name: str
    sensor_name: str
    current_value: float
    threshold: float
    ai_confidence: float = Field(ge=0, le=100)
    failure_description: str
    predicted_failure_date: datetime | None = None
    status: NotificationStatus = "PROPOSED"
    created_at: datetime
    reviewed_by: str | None = None
    review_comments: str | None = None
    review_date: datetime | None = None
    sap_notification_number: str | None = None
    sap_creation_date: datetime | None = None


class NotificationApprovalRequest(BaseModel):
    reviewer_name: str = Field(min_length=1)
    comments: str | None = None


class NotificationRejectionRequest(BaseModel):
    reviewer_name: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class SAPNotificationFormPayload(BaseModel):
    """Pre-filled SAP M1 notification form data.

    The field names stay frontend-friendly while the SAP adapter can later map
    this stable payload to RFC/BAPI/OData fields for IW21 creation.
    """

    functional_location: str
    equipment: str
    planner_group: str
    work_center: str
    reported_by: str = "Saleem AI"
    description: str
    user_status: str = "Call out"
    breakdown_duration: float = 0.0
    unsafepotential_risk: bool = False
    proposal_id: UUID
    asset_id: int
    component_id: int


class CreateSAPNotificationRequest(BaseModel):
    sap_form_data: SAPNotificationFormPayload


class SAPNotificationResponse(BaseModel):
    proposal_id: UUID
    status: NotificationStatus
    sap_notification_number: str
    message: str
    sap_form_data: SAPNotificationFormPayload
