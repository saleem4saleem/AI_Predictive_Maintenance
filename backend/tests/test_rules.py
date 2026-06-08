from __future__ import annotations

import pytest

from app.rules.rule_executor import evaluate_condition, execute_rules
from app.rules.rule_loader import DEFAULT_RULES_PATH, load_rules
from app.rules.rule_validator import validate_rule, validate_rules
from app.services.rules_service import evaluate_rules, flatten_rule_actions


def _base_context() -> dict:
    return {
        "asset_id": 6,
        "asset_code": "PACKAGING_001",
        "asset_type": "Packaging Machine",
        "vibration": 1.0,
        "temperature": 40.0,
        "pressure": 6.0,
        "current_value": 10.0,
        "speed": 1200.0,
        "flow": 60.0,
        "alarm_count_24h": 0,
        "overdue_pm_days": 0,
        "vibration_trend_24h": 0.2,
    }


def test_rules_yaml_exists_and_validates() -> None:
    assert DEFAULT_RULES_PATH.exists()
    rules = load_rules()
    validate_rules(rules)
    assert len(rules) >= 10


@pytest.mark.parametrize(
    ("operator", "actual", "expected", "result"),
    [
        (">", 10, 8, True),
        (">=", 8, 8, True),
        ("<", 2, 3, True),
        ("<=", 3, 3, True),
        ("==", "Packaging Machine", "Packaging Machine", True),
        ("!=", "Furnace", "Packaging Machine", True),
        ("contains", "bearing wear detected", "bearing", True),
    ],
)
def test_supported_operators_work(operator: str, actual: object, expected: object, result: bool) -> None:
    assert evaluate_condition({"field": "value", "operator": operator, "value": expected}, {"value": actual}) is result


def test_invalid_operator_raises_clean_error() -> None:
    with pytest.raises(ValueError, match="unsupported operator"):
        validate_rule(
            {
                "id": "bad_rule",
                "name": "Bad rule",
                "conditions": {"all": [{"field": "vibration", "operator": "eval", "value": 1}]},
                "severity": "low",
                "findings": [],
                "likely_causes": [],
                "recommended_actions": [],
            }
        )


def test_high_vibration_temperature_rule_matches() -> None:
    context = {**_base_context(), "vibration": 8.7, "temperature": 90}
    result = execute_rules(context)

    assert "high_vibration_high_temperature" in [rule["id"] for rule in result["matched_rules"]]
    assert result["severity"] == "high"


def test_low_pressure_low_flow_rule_matches() -> None:
    context = {**_base_context(), "pressure": 2.0, "flow": 21}
    result = execute_rules(context)

    assert "low_pressure_low_flow" in [rule["id"] for rule in result["matched_rules"]]


def test_high_current_low_speed_rule_matches_and_sets_critical() -> None:
    context = {**_base_context(), "current_value": 25, "speed": 900}
    result = execute_rules(context)

    assert "high_current_low_speed" in [rule["id"] for rule in result["matched_rules"]]
    assert result["severity"] == "critical"


def test_repeated_alarms_and_overdue_pm_rules_match() -> None:
    context = {**_base_context(), "alarm_count_24h": 6, "overdue_pm_days": 3}
    result = execute_rules(context)
    ids = [rule["id"] for rule in result["matched_rules"]]

    assert "repeated_alarms" in ids
    assert "overdue_preventive_maintenance" in ids


def test_packaging_vacuum_issue_rule_matches() -> None:
    context = {**_base_context(), "pressure": 2.4, "flow": 21}
    result = execute_rules(context)

    assert "packaging_vacuum_issue" in [rule["id"] for rule in result["matched_rules"]]
    assert any("suction cups" in action for action in result["recommended_actions"])


def test_missing_fields_do_not_crash_engine() -> None:
    result = execute_rules({"asset_id": 1})

    assert result["matched_rules"] == []
    assert result["severity"] == "unknown"


def test_legacy_evaluate_rules_still_returns_recommendations() -> None:
    results = evaluate_rules(
        {
            "vibration": 8.5,
            "temperature": 95.0,
            "pressure": 6.0,
            "current_value": 10.0,
            "speed": 1200.0,
            "flow": 70.0,
            "runtime_hours": 1000.0,
        }
    )
    actions = flatten_rule_actions(results)

    assert actions
    assert any("bearing" in action.lower() or "lubrication" in action.lower() for action in actions)
