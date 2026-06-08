from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.contracts.asset_component_contract import (
    AssetComponent,
    AssetComponentsResponse,
    ComponentDetailResponse,
    ComponentMaintenanceHistory,
    ComponentUpcomingTask,
)
from app.core.config import PROJECT_ROOT
from app.exceptions import ResourceNotFoundError
from app.services.asset_service import get_asset
from app.services.sensor_service import get_latest_sensor_data


COMPONENTS_PATH = PROJECT_ROOT / "data" / "sample" / "sample_asset_components.csv"
COMPONENT_HISTORY_PATH = PROJECT_ROOT / "data" / "sample" / "sample_component_maintenance_history.csv"
COMPONENT_SCHEDULE_PATH = PROJECT_ROOT / "data" / "sample" / "sample_maintenance_schedule.csv"


def get_components_by_asset(asset_id: int | str) -> AssetComponentsResponse:
    """Return maintainable components for an asset.

    The current source is CSV demo data. Later this service can read SAP PM
    functional locations, equipment, work orders, and a database without
    changing the frontend-facing response shape.
    """

    asset = get_asset(asset_id)
    components = [
        component
        for component in _load_components()
        if component.asset_id == int(asset.asset_id)
    ]
    return AssetComponentsResponse(asset_id=int(asset.asset_id), components=components)


def get_component_by_id(component_id: int | str) -> AssetComponent:
    normalized = int(component_id)
    for component in _load_components():
        if component.component_id == normalized:
            return component
    raise ResourceNotFoundError(f"Component '{component_id}' was not found.")


def get_component_maintenance_history(component_id: int | str) -> list[ComponentMaintenanceHistory]:
    component = get_component_by_id(component_id)
    return [
        history
        for history in _load_component_history()
        if history.component_id == component.component_id
    ]


def get_asset_maintenance_history(asset_id: int | str) -> list[ComponentMaintenanceHistory]:
    asset = get_asset(asset_id)
    history = [
        item
        for item in _load_component_history()
        if _history_asset_id(item) == int(asset.asset_id)
    ]
    return sorted(history, key=lambda item: item.date, reverse=True)


def get_component_upcoming_tasks(component_id: int | str) -> list[ComponentUpcomingTask]:
    component = get_component_by_id(component_id)
    tasks = [
        task
        for task in _load_component_schedule()
        if task.component_id == component.component_id
    ]
    return sorted(tasks, key=lambda task: task.planned_date)


def get_asset_upcoming_tasks(asset_id: int | str) -> list[ComponentUpcomingTask]:
    asset = get_asset(asset_id)
    tasks = [
        task
        for task in _load_component_schedule()
        if task.asset_id == int(asset.asset_id)
    ]
    return sorted(tasks, key=lambda task: task.planned_date)


def get_frequent_failures_for_component(component_id: int | str) -> list[str]:
    component = get_component_by_id(component_id)
    if component.frequent_failures:
        return component.frequent_failures

    failures = [
        history.failure_cause
        for history in get_component_maintenance_history(component.component_id)
        if history.failure_cause
    ]
    return list(dict.fromkeys(failures))


def get_component_strategy_assessment(component_id: int | str) -> str:
    component = get_component_by_id(component_id)
    history = get_component_maintenance_history(component.component_id)

    if not component.has_sensor_data:
        if len(history) >= 2:
            return (
                "AI can compare actual failure timing, replacement interval, and feedback "
                "to improve the recommended maintenance interval over time."
            )
        return (
            "AI learning status: More maintenance history and technician feedback are "
            "needed to optimize this maintenance interval."
        )

    if component.condition in {"warning", "critical", "attention"}:
        return (
            "Condition monitoring is available. Review sensor trend, recent work orders, "
            "and repeated failure causes before the next production window."
        )

    return (
        "Condition monitoring is available. Continue comparing sensor behavior with "
        "maintenance history and technician feedback."
    )


def get_component_detail(asset_id: int | str, component_id: int | str) -> ComponentDetailResponse:
    asset = get_asset(asset_id)
    component = get_component_by_id(component_id)
    if component.asset_id != int(asset.asset_id):
        raise ResourceNotFoundError(
            f"Component '{component_id}' does not belong to asset '{asset_id}'."
        )

    history = get_component_maintenance_history(component.component_id)
    upcoming_tasks = get_component_upcoming_tasks(component.component_id)
    sensor_summary = _build_component_sensor_summary(component) if component.has_sensor_data else None
    strategy_assessment = get_component_strategy_assessment(component.component_id)

    return ComponentDetailResponse(
        component=component,
        maintenance_history=history,
        upcoming_tasks=upcoming_tasks,
        frequent_failures=get_frequent_failures_for_component(component.component_id),
        ai_recommendation=_build_ai_recommendation(component, history, upcoming_tasks, strategy_assessment),
        sensor_summary=sensor_summary,
        strategy_assessment=strategy_assessment,
    )


@lru_cache
def _load_components() -> tuple[AssetComponent, ...]:
    if not COMPONENTS_PATH.exists():
        return tuple()

    with COMPONENTS_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return tuple(_component_from_row(row) for row in reader)


@lru_cache
def _load_component_history() -> tuple[ComponentMaintenanceHistory, ...]:
    if not COMPONENT_HISTORY_PATH.exists():
        return tuple()

    with COMPONENT_HISTORY_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return tuple(_history_from_row(row) for row in reader)


@lru_cache
def _load_component_schedule() -> tuple[ComponentUpcomingTask, ...]:
    if not COMPONENT_SCHEDULE_PATH.exists():
        return tuple()

    with COMPONENT_SCHEDULE_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return tuple(_task_from_row(row) for row in reader)


def _component_from_row(row: dict[str, str]) -> AssetComponent:
    return AssetComponent(
        component_id=int(row["component_id"]),
        asset_id=int(row["asset_id"]),
        component_code=row["component_code"],
        component_name=row["component_name"],
        component_type=row["component_type"],
        description=_optional_text(row.get("description")),
        criticality=row["criticality"],
        condition=row["condition"],
        health_score=_optional_float(row.get("health_score")),
        has_sensor_data=_to_bool(row.get("has_sensor_data")),
        has_cbm=_to_bool(row.get("has_cbm")),
        maintenance_strategy=row["maintenance_strategy"],
        maintenance_interval_days=_optional_int(row.get("maintenance_interval_days")),
        last_maintenance_date=_optional_text(row.get("last_maintenance_date")),
        next_planned_maintenance=_optional_text(row.get("next_planned_maintenance")),
        frequent_failures=_split_list(row.get("frequent_failures")),
        recommended_action=_optional_text(row.get("recommended_action")),
    )


def _history_from_row(row: dict[str, str]) -> ComponentMaintenanceHistory:
    return ComponentMaintenanceHistory(
        history_id=int(row["history_id"]),
        component_id=int(row["component_id"]),
        date=row["date"],
        work_order_id=_optional_text(row.get("work_order_id")),
        failure_description=_optional_text(row.get("failure_description")),
        failure_cause=_optional_text(row.get("failure_cause")),
        action_taken=row["action_taken"],
        replaced_part=_optional_text(row.get("replaced_part")),
        downtime_hours=_optional_float(row.get("downtime_hours")),
        technician_note=_optional_text(row.get("technician_note")),
    )


def _task_from_row(row: dict[str, str]) -> ComponentUpcomingTask:
    return ComponentUpcomingTask(
        schedule_id=int(row["schedule_id"]),
        component_id=_optional_int(row.get("component_id")),
        asset_id=int(row["asset_id"]),
        component_code=_optional_text(row.get("component_code")),
        task_name=row["task_name"],
        planned_date=row["planned_date"],
        frequency=_optional_text(row.get("frequency")),
        last_completed_date=_optional_text(row.get("last_completed_date")),
        recommended_interval_days=_optional_int(row.get("recommended_interval_days")),
        priority=row["priority"],
        status=row["status"],
        maintenance_strategy=_optional_text(row.get("maintenance_strategy")),
        ai_recommended_date=_optional_text(row.get("ai_recommended_date")),
        ai_reason=_optional_text(row.get("ai_reason")),
    )


def _build_component_sensor_summary(component: AssetComponent) -> dict[str, Any]:
    latest = get_latest_sensor_data(component.asset_id)
    values = _model_to_dict(latest)
    values["cbm_status"] = "Condition monitoring available"
    values["component_code"] = component.component_code
    return values


def _build_ai_recommendation(
    component: AssetComponent,
    history: list[ComponentMaintenanceHistory],
    upcoming_tasks: list[ComponentUpcomingTask],
    strategy_assessment: str,
) -> str:
    if component.recommended_action:
        recommendation = component.recommended_action
    elif component.frequent_failures:
        recommendation = f"Inspect for {component.frequent_failures[0]} and review recent history."
    else:
        recommendation = "Continue planned maintenance and capture technician feedback."

    task_note = _build_task_note(upcoming_tasks)

    if component.has_sensor_data:
        return (
            f"{recommendation} Use sensor and CBM trend data together with work order history. "
            f"{task_note} {strategy_assessment}"
        )

    history_note = "component history" if history else "maintenance strategy"
    return (
        f"{recommendation} No direct sensor data is available, so the recommendation is based on "
        f"{history_note}, replacement interval, inspection results, and technician feedback. "
        f"{task_note} {strategy_assessment}"
    )


def _build_task_note(upcoming_tasks: list[ComponentUpcomingTask]) -> str:
    if not upcoming_tasks:
        return "No upcoming component task is currently available in the sample schedule."

    urgent = [
        task
        for task in upcoming_tasks
        if task.priority in {"high", "critical"} or task.status in {"due_soon", "overdue"}
    ]
    task = urgent[0] if urgent else upcoming_tasks[0]
    if task.ai_reason:
        return (
            f"Upcoming task: {task.task_name} is {task.status} for {task.planned_date}; "
            f"AI timing note: {task.ai_reason}."
        )
    return f"Upcoming task: {task.task_name} is {task.status} for {task.planned_date}."


def _model_to_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return dict(model.model_dump())
    if hasattr(model, "dict"):
        return dict(model.dict())
    return dict(model)


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _optional_float(value: str | None) -> float | None:
    value = _optional_text(value)
    return None if value is None else float(value)


def _optional_int(value: str | None) -> int | None:
    value = _optional_text(value)
    return None if value is None else int(value)


def _to_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _split_list(value: str | None) -> list[str]:
    value = _optional_text(value)
    if value is None:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _history_asset_id(history: ComponentMaintenanceHistory) -> int | None:
    for component in _load_components():
        if component.component_id == history.component_id:
            return component.asset_id
    return None
