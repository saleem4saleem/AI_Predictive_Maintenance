from __future__ import annotations

from fastapi import APIRouter

from app.contracts.prediction_contract import PredictionResponse, PredictionRunRequest
from app.services.prediction_service import get_prediction, run_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{asset_id}", response_model=PredictionResponse)
async def read_prediction(asset_id: str) -> PredictionResponse:
    return get_prediction(asset_id)


@router.post("/run", response_model=PredictionResponse)
async def run_prediction_for_asset(request: PredictionRunRequest) -> PredictionResponse:
    return run_prediction(request.asset_id)
