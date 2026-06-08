from __future__ import annotations

from typing import Any

from app.contracts.base_response_contract import utc_now
from app.contracts.feedback_contract import FeedbackCreateContract, FeedbackResponseContract
from app.core.config import PROJECT_ROOT
from app.exceptions import InvalidRequestError
from app.services.asset_service import get_asset
from app.services.feedback_learning_service import (
    prepare_feedback_record,
    save_feedback_record,
)
from app.utils.logging_utils import (
    log_feedback_received,
    log_feedback_validation_error,
)

FEEDBACK_PATH = PROJECT_ROOT / "data" / "sample" / "sample_feedback.csv"
VALID_TIMING_FEEDBACK = {"too_early", "correct", "too_late", "not_applicable"}


def submit_feedback(feedback_data: FeedbackCreateContract | dict[str, Any]) -> FeedbackResponseContract:
    """Accept technician feedback and store it for future learning.

    The route contract stays stable while storage remains a CSV fallback. Later
    this service can save to PostgreSQL and trigger training-data preparation
    without changing frontend payloads.
    """

    payload = _normalize_payload(feedback_data)
    _validate_payload(payload)
    get_asset(payload["asset_id"])
    log_feedback_received(int(payload["asset_id"]))

    feedback_record = prepare_feedback_record(payload)
    save_feedback_record(feedback_record, storage_path=FEEDBACK_PATH)

    return FeedbackResponseContract(
        feedback_id=str(feedback_record["feedback_id"]),
        asset_id=int(payload["asset_id"]),
        status="accepted",
        message="Feedback received successfully",
        received_at=utc_now(),
    )


def _normalize_payload(feedback_data: FeedbackCreateContract | dict[str, Any]) -> dict[str, Any]:
    if hasattr(feedback_data, "model_dump"):
        raw_payload = feedback_data.model_dump()
    else:
        raw_payload = dict(feedback_data)

    return {
        key: _empty_string_to_none(value)
        for key, value in raw_payload.items()
    }


def _validate_payload(payload: dict[str, Any]) -> None:
    if payload.get("asset_id") is None:
        _raise_invalid("asset_id is required.")

    try:
        payload["asset_id"] = int(payload["asset_id"])
    except (TypeError, ValueError):
        _raise_invalid("asset_id must be an integer.")

    timing_feedback = payload.get("timing_feedback")
    if timing_feedback is not None and timing_feedback not in VALID_TIMING_FEEDBACK:
        _raise_invalid(
            "timing_feedback must be one of: too_early, correct, too_late, not_applicable."
        )


def _empty_string_to_none(value: Any) -> Any:
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _raise_invalid(message: str) -> None:
    log_feedback_validation_error(message)
    raise InvalidRequestError(message)
