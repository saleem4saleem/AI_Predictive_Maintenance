from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AssetComponent(BaseModel):
    component_id: int
    asset_id: int
    component_code: str
    component_name: str
    component_type: str
    description: str | None = None
    criticality: str
    condition: str
    health_score: float | None = Field(default=None, ge=0, le=100)
    has_sensor_data: bool
    has_cbm: bool
    maintenance_strategy: str
    maintenance_interval_days: int | None = None
    last_maintenance_date: str | None = None
    next_planned_maintenance: str | None = None
    frequent_failures: list[str] = Field(default_factory=list)
    recommended_action: str | None = None


class ComponentMaintenanceHistory(BaseModel):
    history_id: int
    component_id: int
    date: str
    work_order_id: str | None = None
    failure_description: str | None = None
    failure_cause: str | None = None
    action_taken: str
    replaced_part: str | None = None
    downtime_hours: float | None = None
    technician_note: str | None = None


class ComponentUpcomingTask(BaseModel):
    schedule_id: int
    component_id: int | None = None
    asset_id: int
    component_code: str | None = None
    task_name: str
    planned_date: str
    frequency: str | None = None
    last_completed_date: str | None = None
    recommended_interval_days: int | None = None
    priority: str
    status: str
    maintenance_strategy: str | None = None
    ai_recommended_date: str | None = None
    ai_reason: str | None = None


class AssetComponentsResponse(BaseModel):
    asset_id: int
    components: list[AssetComponent]


class ComponentDetailResponse(BaseModel):
    component: AssetComponent
    maintenance_history: list[ComponentMaintenanceHistory]
    upcoming_tasks: list[ComponentUpcomingTask] = Field(default_factory=list)
    frequent_failures: list[str]
    ai_recommendation: str
    sensor_summary: dict[str, Any] | None = None
    strategy_assessment: str | None = None
