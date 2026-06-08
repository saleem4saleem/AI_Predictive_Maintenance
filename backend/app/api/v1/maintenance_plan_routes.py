from __future__ import annotations

from fastapi import APIRouter

from app.contracts.maintenance_plan_contract import MaintenancePlanResponse
from app.services.maintenance_planning_service import get_maintenance_plan

router = APIRouter(prefix="/maintenance-plans", tags=["maintenance-plans"])


@router.get("/{asset_id}", response_model=MaintenancePlanResponse)
async def read_maintenance_plan(asset_id: str) -> MaintenancePlanResponse:
    return get_maintenance_plan(asset_id)
