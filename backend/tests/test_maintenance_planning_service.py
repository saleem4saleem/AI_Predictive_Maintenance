from __future__ import annotations

from datetime import date, timedelta

from app.contracts.maintenance_plan_contract import MaintenancePlanResponse
from app.services.asset_service import get_asset
from app.services.maintenance_planning_service import (
    evaluate_maintenance_timing,
    get_maintenance_plan,
    get_preventive_interval_days,
)


def test_low_risk_asset_keeps_planned_maintenance() -> None:
    plan = get_maintenance_plan(1)

    assert isinstance(plan, MaintenancePlanResponse)
    assert plan.recommendation == "keep planned maintenance"
    assert plan.priority == "normal"
    assert plan.next_planned_maintenance
    assert plan.preventive_interval_days == 14


def test_short_remaining_life_triggers_urgent_inspection() -> None:
    plan = get_maintenance_plan(6, remaining_useful_life_days=5)

    assert plan.recommendation == "urgent inspection needed"
    assert plan.priority == "urgent"
    assert plan.ai_recommended_maintenance
    assert plan.planned_vs_predicted_status == "predicted_before_planned"


def test_predicted_failure_before_plan_moves_maintenance_earlier() -> None:
    asset = get_asset(5)
    today = date.today()

    decision = evaluate_maintenance_timing(
        asset=asset,
        next_planned_date=today + timedelta(days=28),
        ai_recommended_date=today + timedelta(days=12),
        remaining_useful_life_days=12,
        overdue_pm_days=0,
        open_work_orders=1,
    )

    assert decision["recommendation"] == "move maintenance earlier"
    assert decision["priority"] == "high"
    assert decision["planned_vs_predicted_status"] == "predicted_before_planned"


def test_overdue_high_criticality_asset_is_urgent() -> None:
    plan = get_maintenance_plan(3)

    assert plan.recommendation == "urgent inspection needed"
    assert plan.priority == "urgent"
    assert plan.open_work_orders == 3
    assert "overdue" in plan.reason.lower()


def test_preventive_interval_uses_asset_criticality() -> None:
    furnace = get_asset(1)
    packaging = get_asset(6)

    assert get_preventive_interval_days(furnace) == 14
    assert get_preventive_interval_days(packaging) == 28
