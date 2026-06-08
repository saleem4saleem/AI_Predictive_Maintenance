from __future__ import annotations

import app.services.rules_service as rules_service
from app.services.rules_service import evaluate_maintenance_rules


def test_rules_service_returns_safe_structure() -> None:
    result = evaluate_maintenance_rules(
        {
            "asset_id": 6,
            "asset_code": "PACKAGING_001",
            "asset_type": "Packaging Machine",
            "vibration": 8.7,
            "temperature": 78,
            "pressure": 2.4,
            "current_value": 16,
            "speed": 1200,
            "flow": 21,
            "alarm_count_24h": 6,
            "overdue_pm_days": 3,
            "vibration_trend_24h": 1.8,
        }
    )

    assert set(result) >= {"matched_rules", "findings", "likely_causes", "recommended_actions", "severity"}
    assert result["matched_rules"]
    assert result["severity"] == "high"
    assert "Inspect suction cups" in result["recommended_actions"]


def test_rules_service_returns_fallback_when_rules_unavailable(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(rules_service, "RULES_PATH", tmp_path / "missing_rules.yaml")

    result = evaluate_maintenance_rules({"vibration": 10})

    assert result["matched_rules"] == []
    assert result["severity"] == "unknown"
    assert "warning" in result
