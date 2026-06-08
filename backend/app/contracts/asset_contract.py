from __future__ import annotations

from pydantic import BaseModel, Field


class AssetBasicResponse(BaseModel):
    asset_id: int
    asset_code: str
    asset_name: str
    asset_type: str
    location: str | None = None
    status: str
    criticality: str
    health_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: str | None = None


class AssetListResponse(BaseModel):
    assets: list[AssetBasicResponse]
    total: int


class AssetContract(BaseModel):
    """Internal demo asset shape kept for existing services.

    Public routes should expose AssetBasicResponse or richer response contracts.
    """

    asset_id: str
    asset_code: str
    asset_name: str
    asset_type: str = "Production Asset"
    location: str = "Demo Glass Factory"
    status: str = "healthy"
    health_score: float = Field(default=90, ge=0, le=100)
    risk_level: str = "low"
    process_area: str
    criticality: int = Field(ge=1, le=100)
    downtime_cost_per_hour: float = Field(ge=0)
    description: str
