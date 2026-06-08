from __future__ import annotations

from pydantic import BaseModel, Field


class PredictionRunRequest(BaseModel):
    asset_id: int


class PredictionResponse(BaseModel):
    asset_id: int
    asset_code: str
    asset_name: str
    health_score: float = Field(ge=0, le=100)
    condition: str
    failure_probability_7_days: float = Field(ge=0, le=1)
    failure_probability_30_days: float = Field(ge=0, le=1)
    predicted_failure_date: str | None = None
    remaining_useful_life_days: int | None
    predicted_failure_mode: str | None
    risk_level: str
    confidence: str
    recommended_action: str
    explanation: str
    model_version: str
    generated_at: str | None = None
    data_quality: str | None = None
    warnings: list[str] = Field(default_factory=list)


PredictionContract = PredictionResponse
