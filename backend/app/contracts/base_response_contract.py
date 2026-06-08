from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseResponseContract(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Request completed successfully.")
    timestamp: datetime = Field(default_factory=utc_now)


class DataResponseContract(BaseResponseContract):
    data: dict[str, Any] = Field(default_factory=dict)


class BaseAPIResponse(BaseModel):
    """Simple optional wrapper for future endpoints that need a status envelope."""

    status: str = "success"
    message: str | None = None
