from __future__ import annotations

from fastapi import APIRouter

from app.contracts.feedback_contract import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import submit_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
async def create_feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    return submit_feedback(feedback)
