from __future__ import annotations

from fastapi import APIRouter

from app.contracts.overview_contract import OverviewResponse
from app.services.overview_service import get_factory_overview

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("", response_model=OverviewResponse)
async def read_overview() -> OverviewResponse:
    return get_factory_overview()
