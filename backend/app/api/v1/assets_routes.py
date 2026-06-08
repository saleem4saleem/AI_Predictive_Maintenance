from __future__ import annotations

from fastapi import APIRouter

from app.contracts.asset_contract import AssetBasicResponse
from app.services.asset_service import get_asset_by_id, get_assets

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetBasicResponse])
async def read_assets() -> list[AssetBasicResponse]:
    return get_assets()


@router.get("/{asset_id}", response_model=AssetBasicResponse)
async def read_asset(asset_id: str) -> AssetBasicResponse:
    return get_asset_by_id(asset_id)
