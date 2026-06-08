from __future__ import annotations

from typing import Any

from app.core.config import BACKEND_DIR
from app.rules.rule_executor import execute_rules
from app.rules.rule_loader import RuleLoadError, load_rules
from app.rules.rule_validator import validate_rules

RULES_PATH = BACKEND_DIR / "app" / "rules" / "maintenance_rules.yaml"


def evaluate_maintenance_rules(context: dict[str, Any]) -> dict[str, Any]:
    try:
        rules = load_rules(RULES_PATH)
        validate_rules(rules)
        return execute_rules(context, rules)
    except (RuleLoadError, ValueError) as exc:
        return {
            "matched_rules": [],
            "findings": [],
            "likely_causes": [],
            "recommended_actions": [],
            "severity": "unknown",
            "warning": f"Rules engine unavailable: {exc}",
        }


def evaluate_rules(features: dict[str, Any], extra_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Compatibility helper for older prediction code that expects a list."""

    context = {**features, **(extra_context or {})}
    return evaluate_maintenance_rules(context).get("matched_rules", [])


def flatten_rule_actions(rule_results: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for result in rule_results:
        actions.extend(result.get("recommended_actions", []))
    return list(dict.fromkeys(actions))


def flatten_rule_causes(rule_results: list[dict[str, Any]]) -> list[str]:
    causes: list[str] = []
    for result in rule_results:
        causes.extend(result.get("likely_causes", []))
    return list(dict.fromkeys(causes))
