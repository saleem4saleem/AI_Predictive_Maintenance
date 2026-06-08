from __future__ import annotations

from fastapi import APIRouter

from app.contracts.recommendation_contract import RecommendationResponse
from app.services.recommendation_service import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{asset_id}", response_model=RecommendationResponse)
async def read_recommendations(asset_id: str) -> RecommendationResponse:
    return get_recommendations(asset_id)
