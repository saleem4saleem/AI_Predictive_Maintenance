from __future__ import annotations

from datetime import date, timedelta

from app.contracts.asset_contract import AssetContract
from app.contracts.maintenance_plan_contract import MaintenancePlanContract
from app.services.asset_service import get_asset


OPEN_WORK_ORDER_COUNTS: dict[str, int] = {
    "1": 0,
    "2": 1,
    "3": 3,
    "4": 0,
    "5": 2,
    "6": 2,
    "7": 1,
    "8": 1,
}

OVERDUE_PM_DAYS: dict[str, int] = {
    "3": 4,
    "6": 1,
}


def get_maintenance_plan(
    asset_or_id: AssetContract | int | str,
    remaining_useful_life_days: int | None = None,
    predicted_failure_date: str | date | None = None,
) -> MaintenancePlanContract:
    """Compare planned PM timing with AI risk timing.

    This service is intentionally rule-based for the MVP. Later it can read SAP
    PM plans, open work orders, and production calendars without changing the
    frontend-facing MaintenancePlanContract.
    """

    asset = asset_or_id if isinstance(asset_or_id, AssetContract) else get_asset(asset_or_id)
    today = date.today()
    preventive_interval_days = get_preventive_interval_days(asset)
    overdue_pm_days = get_overdue_pm_days(asset)
    open_work_orders = get_open_work_order_count(asset)
    next_planned_date = _calculate_next_planned_date(today, preventive_interval_days, overdue_pm_days)
    ai_date = _resolve_ai_recommended_date(today, remaining_useful_life_days, predicted_failure_date)

    decision = evaluate_maintenance_timing(
        asset=asset,
        next_planned_date=next_planned_date,
        ai_recommended_date=ai_date,
        remaining_useful_life_days=remaining_useful_life_days,
        overdue_pm_days=overdue_pm_days,
        open_work_orders=open_work_orders,
    )

    return MaintenancePlanContract(
        asset_id=int(asset.asset_id),
        next_planned_maintenance=next_planned_date.isoformat(),
        ai_recommended_maintenance=ai_date.isoformat() if ai_date else None,
        recommendation=decision["recommendation"],
        priority=decision["priority"],
        reason=decision["reason"],
        planned_vs_predicted_status=decision["planned_vs_predicted_status"],
        next_planned_maintenance_date=next_planned_date.isoformat(),
        preventive_interval_days=preventive_interval_days,
        open_work_orders=open_work_orders,
        ai_recommended_date=ai_date.isoformat() if ai_date else None,
        planning_status=decision["recommendation"],
        timing_advice=decision["reason"],
    )


def get_maintenance_plan_for_asset(asset_id: int | str) -> MaintenancePlanContract:
    return get_maintenance_plan(asset_id)


def evaluate_maintenance_timing(
    asset: AssetContract,
    next_planned_date: date,
    ai_recommended_date: date | None,
    remaining_useful_life_days: int | None,
    overdue_pm_days: int,
    open_work_orders: int,
) -> dict[str, str]:
    """Return maintenance timing advice using reliability planning rules."""

    criticality_label = _criticality_bucket(asset.criticality)

    if remaining_useful_life_days is not None and remaining_useful_life_days <= 7:
        return {
            "recommendation": "urgent inspection needed",
            "priority": "urgent",
            "reason": "Remaining useful life is seven days or less; inspect before the next production window.",
            "planned_vs_predicted_status": "predicted_before_planned",
        }

    if overdue_pm_days > 0 and criticality_label in {"critical", "high"}:
        return {
            "recommendation": "urgent inspection needed",
            "priority": "urgent",
            "reason": f"Preventive maintenance is overdue by {overdue_pm_days} days on a {criticality_label}-criticality asset.",
            "planned_vs_predicted_status": "overdue_preventive_maintenance",
        }

    if ai_recommended_date and ai_recommended_date < next_planned_date:
        days_gap = (next_planned_date - ai_recommended_date).days
        return {
            "recommendation": "move maintenance earlier",
            "priority": "high",
            "reason": f"AI risk timing is {days_gap} days earlier than the current preventive maintenance plan.",
            "planned_vs_predicted_status": "predicted_before_planned",
        }

    if overdue_pm_days > 0:
        return {
            "recommendation": "move maintenance earlier",
            "priority": "high",
            "reason": f"Preventive maintenance is overdue by {overdue_pm_days} days; schedule the task before risk increases.",
            "planned_vs_predicted_status": "overdue_preventive_maintenance",
        }

    if asset.risk_level in {"high", "critical"} or open_work_orders >= 3:
        return {
            "recommendation": "move maintenance earlier",
            "priority": "high",
            "reason": "Asset risk or open work order load is elevated; pull the inspection into the next available maintenance window.",
            "planned_vs_predicted_status": "elevated_risk_before_plan",
        }

    if remaining_useful_life_days is not None and remaining_useful_life_days <= preventive_interval_days:
        return {
            "recommendation": "monitor only",
            "priority": "medium",
            "reason": "Predicted risk is near the preventive interval; monitor daily and keep the plan visible to maintenance.",
            "planned_vs_predicted_status": "risk_near_planned_date",
        }

    return {
        "recommendation": "keep planned maintenance",
        "priority": "normal",
        "reason": "Current preventive maintenance timing is acceptable; continue normal monitoring.",
        "planned_vs_predicted_status": "planned_before_predicted",
    }


def get_preventive_interval_days(asset: AssetContract) -> int:
    """Return a practical PM interval based on criticality and asset type."""

    if asset.criticality >= 95:
        return 14
    if asset.criticality >= 85:
        return 21
    if asset.asset_type in {"Quality Equipment", "Packaging Equipment", "Transport Equipment"}:
        return 28
    return 30


def get_open_work_order_count(asset: AssetContract) -> int:
    return OPEN_WORK_ORDER_COUNTS.get(asset.asset_id, 0)


def get_overdue_pm_days(asset: AssetContract) -> int:
    return OVERDUE_PM_DAYS.get(asset.asset_id, 0)


def _calculate_next_planned_date(today: date, interval_days: int, overdue_pm_days: int) -> date:
    if overdue_pm_days > 0:
        return today - timedelta(days=overdue_pm_days)
    return today + timedelta(days=interval_days)


def _resolve_ai_recommended_date(
    today: date,
    remaining_useful_life_days: int | None,
    predicted_failure_date: str | date | None,
) -> date | None:
    if predicted_failure_date:
        if isinstance(predicted_failure_date, date):
            return predicted_failure_date
        return date.fromisoformat(predicted_failure_date)
    if remaining_useful_life_days is None:
        return None
    return today + timedelta(days=remaining_useful_life_days)


def _criticality_bucket(criticality: int) -> str:
    if criticality >= 95:
        return "critical"
    if criticality >= 85:
        return "high"
    if criticality >= 70:
        return "medium"
    return "low"
