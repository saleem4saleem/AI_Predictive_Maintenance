from __future__ import annotations

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    action: str
    priority: str
    reason: str | None = None
    due_date: str | None = None
    source: str | None = None


class RecommendationResponse(BaseModel):
    asset_id: int
    recommendations: list[RecommendationItem]
    actions: list[str] = []
    priority: str | None = None
    reason: str | None = None


RecommendationActionContract = RecommendationItem
RecommendationContract = RecommendationResponse
