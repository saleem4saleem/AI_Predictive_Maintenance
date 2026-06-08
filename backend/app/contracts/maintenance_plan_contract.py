from __future__ import annotations

from pydantic import BaseModel


class MaintenancePlanResponse(BaseModel):
    asset_id: int
    next_planned_maintenance: str | None = None
    ai_recommended_maintenance: str | None = None
    recommendation: str
    priority: str
    reason: str
    planned_vs_predicted_status: str
    next_planned_maintenance_date: str | None = None
    preventive_interval_days: int | None = None
    open_work_orders: int | None = None
    ai_recommended_date: str | None = None
    planning_status: str | None = None
    timing_advice: str | None = None


MaintenancePlanContract = MaintenancePlanResponse
