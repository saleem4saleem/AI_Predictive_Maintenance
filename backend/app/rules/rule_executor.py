from __future__ import annotations

from typing import Any

from app.rules.rule_loader import load_rules
from app.rules.rule_validator import validate_rules

SEVERITY_ORDER = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def evaluate_condition(condition: dict[str, Any], context: dict[str, Any]) -> bool:
    field = condition["field"]
    operator = condition["operator"]
    expected = condition["value"]

    if field not in context or context[field] is None:
        return False

    actual = context[field]
    if operator == "contains":
        return str(expected).lower() in str(actual).lower()

    if operator in {">", ">=", "<", "<="}:
        try:
            actual_number = float(actual)
            expected_number = float(expected)
        except (TypeError, ValueError):
            return False
        return _compare_numbers(actual_number, operator, expected_number)

    if operator == "==":
        return str(actual) == str(expected)
    if operator == "!=":
        return str(actual) != str(expected)

    raise ValueError(f"Unsupported operator '{operator}'.")


def evaluate_rule(rule: dict[str, Any], context: dict[str, Any]) -> bool:
    conditions = rule.get("conditions", {})
    all_conditions = conditions.get("all")
    any_conditions = conditions.get("any")

    all_match = True
    if all_conditions is not None:
        all_match = all(evaluate_condition(condition, context) for condition in all_conditions)

    any_match = True
    if any_conditions is not None:
        any_match = any(evaluate_condition(condition, context) for condition in any_conditions)

    return all_match and any_match


def execute_rules(context: dict[str, Any], rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    active_rules = rules if rules is not None else load_rules()
    validate_rules(active_rules)

    matched_rules: list[dict[str, Any]] = []
    findings: list[str] = []
    likely_causes: list[str] = []
    recommended_actions: list[str] = []
    highest_severity = "unknown"

    for rule in active_rules:
        if not evaluate_rule(rule, context):
            continue

        matched = {
            "id": rule["id"],
            "name": rule["name"],
            "description": rule.get("description"),
            "severity": rule["severity"],
            "findings": rule["findings"],
            "likely_causes": rule["likely_causes"],
            "recommended_actions": rule["recommended_actions"],
            "tags": rule.get("tags", []),
        }
        matched_rules.append(matched)
        findings.extend(rule["findings"])
        likely_causes.extend(rule["likely_causes"])
        recommended_actions.extend(rule["recommended_actions"])
        highest_severity = _max_severity(highest_severity, rule["severity"])

    return {
        "matched_rules": matched_rules,
        "findings": _dedupe(findings),
        "likely_causes": _dedupe(likely_causes),
        "recommended_actions": _dedupe(recommended_actions),
        "severity": highest_severity,
    }


def _compare_numbers(actual: float, operator: str, expected: float) -> bool:
    if operator == ">":
        return actual > expected
    if operator == ">=":
        return actual >= expected
    if operator == "<":
        return actual < expected
    if operator == "<=":
        return actual <= expected
    raise ValueError(f"Unsupported numeric operator '{operator}'.")


def _max_severity(current: str, candidate: str) -> str:
    return candidate if SEVERITY_ORDER[candidate] > SEVERITY_ORDER[current] else current


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
