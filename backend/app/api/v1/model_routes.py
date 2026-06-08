from __future__ import annotations

from fastapi import APIRouter

from app.contracts.model_contract import ActiveModelResponse
from app.services.model_service import get_active_model

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/active", response_model=ActiveModelResponse)
async def read_active_model() -> ActiveModelResponse:
    return get_active_model()
