from __future__ import annotations

from fastapi import APIRouter

from app.contracts.asset_detail_contract import AssetDetailResponse
from app.services.asset_detail_service import get_asset_detail

router = APIRouter(prefix="/assets", tags=["asset-detail"])


@router.get("/{asset_id}/detail", response_model=AssetDetailResponse)
async def read_asset_detail(asset_id: str) -> AssetDetailResponse:
    return get_asset_detail(asset_id)
