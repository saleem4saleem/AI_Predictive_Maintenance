from __future__ import annotations

from pydantic import BaseModel


class SensorLatestResponse(BaseModel):
    asset_id: int
    timestamp: str | None = None
    vibration: float | None = None
    temperature: float | None = None
    pressure: float | None = None
    current_value: float | None = None
    speed: float | None = None
    flow: float | None = None
    runtime_hours: float | None = None


class SensorHistoryPoint(BaseModel):
    timestamp: str
    vibration: float | None = None
    temperature: float | None = None
    pressure: float | None = None
    current_value: float | None = None
    speed: float | None = None
    flow: float | None = None
    runtime_hours: float | None = None


class SensorHistoryResponse(BaseModel):
    asset_id: int
    history: list[SensorHistoryPoint]
