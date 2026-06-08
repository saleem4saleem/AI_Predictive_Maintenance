from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.contracts.sensor_contract import SensorHistoryPoint, SensorHistoryResponse, SensorLatestResponse
from app.core.config import PROJECT_ROOT
from app.services.asset_service import get_asset

SAMPLE_SENSOR_PATH = PROJECT_ROOT / "data" / "sample" / "sample_sensor_data.csv"
SENSOR_FIELDS = ["vibration", "temperature", "pressure", "current_value", "speed", "flow", "runtime_hours"]


@lru_cache
def _load_sensor_rows() -> tuple[dict[str, Any], ...]:
    if not SAMPLE_SENSOR_PATH.exists():
        return tuple()

    with SAMPLE_SENSOR_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows: list[dict[str, Any]] = []
        for row in reader:
            normalized = dict(row)
            for field in SENSOR_FIELDS:
                normalized[field] = float(normalized[field])
            rows.append(normalized)
        return tuple(rows)


def get_sensor_history_rows(asset_id: str | int, limit: int = 24) -> list[dict[str, Any]]:
    asset = get_asset(asset_id)
    rows = [dict(row) for row in _load_sensor_rows() if row.get("asset_code") == asset.asset_code]
    return rows[-limit:]


def get_latest_sensor_values(asset_id: str | int) -> dict[str, float]:
    history = get_sensor_history_rows(asset_id, limit=1)
    if not history:
        return {field: 0.0 for field in SENSOR_FIELDS}
    latest = history[-1]
    return {field: float(latest[field]) for field in SENSOR_FIELDS}


def get_latest_sensor_data(asset_id: int | str) -> SensorLatestResponse:
    asset = get_asset(asset_id)
    history = get_sensor_history_rows(asset.asset_id, limit=1)
    if not history:
        return SensorLatestResponse(asset_id=int(asset.asset_id), timestamp=None)

    latest = history[-1]
    return SensorLatestResponse(
        asset_id=int(asset.asset_id),
        timestamp=str(latest.get("timestamp")),
        vibration=float(latest["vibration"]),
        temperature=float(latest["temperature"]),
        pressure=float(latest["pressure"]),
        current_value=float(latest["current_value"]),
        speed=float(latest["speed"]),
        flow=float(latest["flow"]),
        runtime_hours=float(latest["runtime_hours"]),
    )


def get_sensor_history(asset_id: int | str, limit: int = 24) -> SensorHistoryResponse:
    asset = get_asset(asset_id)
    rows = get_sensor_history_rows(asset.asset_id, limit=limit)
    return SensorHistoryResponse(
        asset_id=int(asset.asset_id),
        history=[
            SensorHistoryPoint(
                timestamp=str(row.get("timestamp")),
                vibration=float(row["vibration"]),
                temperature=float(row["temperature"]),
                pressure=float(row["pressure"]),
                current_value=float(row["current_value"]),
                speed=float(row["speed"]),
                flow=float(row["flow"]),
                runtime_hours=float(row["runtime_hours"]),
            )
            for row in rows
        ],
    )


def summarize_sensors(asset_id: str | int) -> dict[str, Any]:
    values = get_latest_sensor_values(asset_id)
    alerts = []
    if values["vibration"] >= 7:
        alerts.append("High vibration")
    if values["temperature"] >= 90 and values["vibration"] >= 5:
        alerts.append("Temperature and vibration are elevated")
    if values["pressure"] <= 5:
        alerts.append("Low pressure")
    if values["current_value"] >= 180 and values["speed"] <= 80:
        alerts.append("High current with low speed")
    if values["flow"] <= 45:
        alerts.append("Low flow")
    return {"latest": values, "alerts": alerts, "sample_count": len(get_sensor_history_rows(asset_id))}
