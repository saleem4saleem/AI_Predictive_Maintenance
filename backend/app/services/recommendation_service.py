from __future__ import annotations

from app.contracts.asset_contract import AssetContract
from app.contracts.recommendation_contract import RecommendationItem, RecommendationResponse
from app.services.asset_service import get_asset


def build_recommendation(
    asset: AssetContract,
    risk_level: str,
    failure_mode: str,
    planning_status: str,
    rule_actions: list[str],
    similar_case_actions: list[str],
) -> dict:
    actions = []
    failure_mode = failure_mode or "needs validation"
    if "bearing" in failure_mode or "lubrication" in failure_mode:
        actions.extend(["Inspect bearing condition", "Check lubrication level and contamination", "Verify alignment"])
    elif "blockage" in failure_mode or "leakage" in failure_mode:
        actions.extend(["Inspect filter and valves", "Check for leakage", "Verify pump or pneumatic pressure"])
    elif "overload" in failure_mode or "drive" in failure_mode:
        actions.extend(["Inspect motor load", "Check mechanical blockage", "Review drive parameters"])
    else:
        actions.append(f"Inspect {asset.asset_name} using the next shutdown checklist")

    actions.extend(rule_actions)
    actions.extend(similar_case_actions[:2])

    if planning_status in {"urgent inspection needed", "move maintenance earlier"}:
        actions.append("Move maintenance before predicted risk date")
    if risk_level == "low":
        actions = [f"Continue monitoring {asset.asset_name}", "Keep planned preventive maintenance"]

    deduped_actions = list(dict.fromkeys(actions))
    return {
        "asset_id": asset.asset_id,
        "actions": deduped_actions,
        "priority": "urgent" if risk_level == "critical" else risk_level,
        "reason": f"Risk level is {risk_level}; likely failure mode is {failure_mode}.",
    }


def get_recommendations(asset_id: int | str) -> RecommendationResponse:
    asset = get_asset(asset_id)
    priority = "high" if asset.risk_level in {"high", "critical"} else asset.risk_level
    due_date = _due_date_for_priority(priority)
    items = [
        RecommendationItem(
            action=_default_action(asset),
            priority=priority,
            reason=f"{asset.asset_name} is currently {asset.status} with {asset.risk_level} risk.",
            due_date=due_date,
            source="service_placeholder",
        )
    ]

    if asset.status == "attention":
        items.append(
            RecommendationItem(
                action="Review latest sensor trend and open maintenance actions",
                priority="medium",
                reason="Attention state should be validated before the next production window.",
                due_date=_due_date_for_priority("medium"),
                source="service_placeholder",
            )
        )

    return RecommendationResponse(
        asset_id=int(asset.asset_id),
        recommendations=items,
        actions=[item.action for item in items],
        priority=priority,
        reason=items[0].reason,
    )


def _default_action(asset: AssetContract) -> str:
    if asset.risk_level == "low":
        return "Continue normal monitoring"
    if asset.asset_name == "IS Forming Machine":
        return "Inspect forming section wear points, lubrication, and pneumatic response"
    if asset.asset_name == "Packaging Machine":
        return "Inspect suction cups, sealing temperature, labels, and transport timing"
    if asset.asset_name == "Inspection Machine":
        return "Check camera cleanliness, reject timing, and scanner calibration"
    return f"Inspect {asset.asset_name} during the next planned maintenance window"


def _due_date_for_priority(priority: str) -> str:
    from datetime import date, timedelta

    days = 3 if priority in {"high", "critical", "urgent"} else 14
    return (date.today() + timedelta(days=days)).isoformat()
