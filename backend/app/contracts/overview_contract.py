from __future__ import annotations

from pydantic import BaseModel, Field


class ProductionFlowAsset(BaseModel):
    asset_id: int
    asset_code: str
    asset_name: str
    status: str
    health_score: float = Field(ge=0, le=100)
    risk_level: str
    predicted_failure_date: str | None = None
    next_planned_maintenance: str | None = None
    ai_recommended_maintenance: str | None = None


class AssetOverviewCard(BaseModel):
    asset_id: int
    asset_code: str
    asset_name: str
    asset_type: str
    status: str
    health_score: float = Field(ge=0, le=100)
    risk_level: str
    criticality: str
    open_actions: int
    predicted_failure_date: str | None = None


class OverviewResponse(BaseModel):
    factory_name: str
    factory_health: float = Field(ge=0, le=100)
    critical_assets: int
    open_actions: int
    weekly_downtime_risk_hours: float
    production_flow: list[ProductionFlowAsset]
    assets: list[AssetOverviewCard]


OverviewAssetContract = ProductionFlowAsset
OverviewContract = OverviewResponse
