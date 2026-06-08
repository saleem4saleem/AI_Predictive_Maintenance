from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ActiveModelResponse(BaseModel):
    model_type: str
    version: str
    status: str
    trained_at: str | None = None
    features: list[str]
    target_type: str | None = None
    model_file_exists: bool | None = None
    scaler_file_exists: bool | None = None
    component: str | None = None
    ok: bool | None = None
    detail: str | None = None
    model_version: str | None = None
    metrics: dict[str, Any] | None = None


ActiveModelContract = ActiveModelResponse
