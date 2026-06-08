from __future__ import annotations

from fastapi import APIRouter

from app.contracts.asset_component_contract import (
    AssetComponentsResponse,
    ComponentDetailResponse,
)
from app.services.asset_component_service import (
    get_component_detail,
    get_components_by_asset,
)

router = APIRouter(prefix="/assets", tags=["asset-components"])


@router.get("/{asset_id}/components", response_model=AssetComponentsResponse)
async def read_asset_components(asset_id: str) -> AssetComponentsResponse:
    return get_components_by_asset(asset_id)


@router.get("/{asset_id}/components/{component_id}", response_model=ComponentDetailResponse)
async def read_asset_component_detail(
    asset_id: str,
    component_id: str,
) -> ComponentDetailResponse:
    return get_component_detail(asset_id, component_id)
