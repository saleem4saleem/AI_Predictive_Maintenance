from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.contracts.base_response_contract import utc_now


class ErrorDetailContract(BaseModel):
    code: str = Field(..., description="Stable application error code.")
    message: str = Field(..., description="Human-readable error message.")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured debugging context safe to return to clients.",
    )


class ErrorResponseContract(BaseModel):
    success: bool = Field(default=False)
    error: ErrorDetailContract
    timestamp: datetime = Field(default_factory=utc_now)


class ErrorResponse(BaseModel):
    """Frontend-friendly error shape for future routes that do not use envelopes."""

    detail: str
    error_code: str | None = None
    path: str | None = None
    timestamp: str | None = None
