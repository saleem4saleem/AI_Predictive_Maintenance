from __future__ import annotations

from fastapi import APIRouter

from app.contracts.sensor_contract import SensorHistoryResponse, SensorLatestResponse
from app.services.sensor_service import get_latest_sensor_data, get_sensor_history

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/{asset_id}", response_model=SensorLatestResponse)
async def read_latest_sensors(asset_id: str) -> SensorLatestResponse:
    return get_latest_sensor_data(asset_id)


@router.get("/{asset_id}/history", response_model=SensorHistoryResponse)
async def read_sensor_history(asset_id: str, limit: int = 24) -> SensorHistoryResponse:
    return get_sensor_history(asset_id, limit=limit)
