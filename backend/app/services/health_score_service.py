from __future__ import annotations

from app.contracts.asset_contract import AssetContract


def calculate_health_score(asset: AssetContract, anomaly_score: float, sensor_severity: float) -> float:
    criticality_penalty = asset.criticality / 100 * 8
    score = 100 - anomaly_score * 42 - sensor_severity * 35 - criticality_penalty
    return round(max(0.0, min(100.0, score)), 1)


def condition_from_health_score(score: float) -> str:
    if score >= 90:
        return "healthy"
    if score >= 70:
        return "normal"
    if score >= 50:
        return "attention"
    if score >= 30:
        return "warning"
    return "critical"
