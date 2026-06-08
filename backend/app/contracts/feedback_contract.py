from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FeedbackRequest(BaseModel):
    asset_id: int
    prediction_id: int | None = None
    was_prediction_correct: bool | None = None
    actual_failure_happened: bool | None = None
    actual_failure_mode: str | None = None
    action_taken: str | None = None
    timing_feedback: str | None = Field(default=None, pattern="^(too_early|correct|too_late|not_applicable)$")
    technician_comment: str | None = None

    @field_validator("prediction_id", mode="before")
    @classmethod
    def normalize_prediction_id(cls, value: object) -> int | None:
        if value is None or value == "":
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None


class FeedbackResponse(BaseModel):
    status: str
    message: str
    asset_id: int
    feedback_id: str | None = None
    received_at: datetime | None = None


FeedbackCreateContract = FeedbackRequest
FeedbackResponseContract = FeedbackResponse
