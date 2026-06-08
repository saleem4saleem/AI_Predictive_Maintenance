from __future__ import annotations

from typing import Any

SUPPORTED_OPERATORS = {">", ">=", "<", "<=", "==", "!=", "contains"}
SEVERITY_VALUES = {"low", "medium", "high", "critical"}
REQUIRED_RULE_FIELDS = {
    "id",
    "name",
    "conditions",
    "severity",
    "findings",
    "likely_causes",
    "recommended_actions",
}


def validate_rule(rule: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_RULE_FIELDS.difference(rule))
    if missing:
        raise ValueError(f"Rule {rule.get('id', '<unknown>')} missing required field(s): {', '.join(missing)}")

    severity = rule.get("severity")
    if severity not in SEVERITY_VALUES:
        raise ValueError(f"Rule {rule['id']} has unsupported severity '{severity}'.")

    for list_field in ["findings", "likely_causes", "recommended_actions"]:
        if not isinstance(rule.get(list_field), list):
            raise ValueError(f"Rule {rule['id']} field '{list_field}' must be a list.")

    _validate_condition_group(rule["id"], rule["conditions"])


def validate_rules(rules: list[dict[str, Any]]) -> None:
    for rule in rules:
        validate_rule(rule)


def _validate_condition_group(rule_id: str, condition_group: dict[str, Any]) -> None:
    if not isinstance(condition_group, dict):
        raise ValueError(f"Rule {rule_id} conditions must be an object.")

    group_keys = [key for key in ["all", "any"] if key in condition_group]
    if not group_keys:
        raise ValueError(f"Rule {rule_id} conditions must include 'all' or 'any'.")

    for group_key in group_keys:
        conditions = condition_group[group_key]
        if not isinstance(conditions, list) or not conditions:
            raise ValueError(f"Rule {rule_id} condition group '{group_key}' must be a non-empty list.")
        for condition in conditions:
            _validate_condition(rule_id, condition)


def _validate_condition(rule_id: str, condition: dict[str, Any]) -> None:
    if not isinstance(condition, dict):
        raise ValueError(f"Rule {rule_id} condition must be an object.")

    for field in ["field", "operator", "value"]:
        if field not in condition:
            raise ValueError(f"Rule {rule_id} condition missing '{field}'.")

    operator = condition["operator"]
    if operator not in SUPPORTED_OPERATORS:
        raise ValueError(f"Rule {rule_id} uses unsupported operator '{operator}'.")
