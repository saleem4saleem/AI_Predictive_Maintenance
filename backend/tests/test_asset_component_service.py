from app.contracts.asset_component_contract import ComponentDetailResponse
from app.exceptions import ResourceNotFoundError
from app.services.asset_component_service import (
    get_asset_maintenance_history,
    get_asset_upcoming_tasks,
    get_component_detail,
    get_component_maintenance_history,
    get_component_upcoming_tasks,
    get_components_by_asset,
)


def test_is_machine_components_include_molds_and_pneumatics() -> None:
    response = get_components_by_asset(3)
    names = {component.component_name for component in response.components}

    assert "Molds" in names
    assert "Pneumatic System" in names


def test_component_without_sensor_data_uses_strategy_and_history() -> None:
    detail = get_component_detail(3, 301)

    assert isinstance(detail, ComponentDetailResponse)
    assert detail.component.component_name == "Molds"
    assert detail.component.has_sensor_data is False
    assert detail.sensor_summary is None
    assert detail.maintenance_history
    assert detail.upcoming_tasks
    assert detail.upcoming_tasks[0].task_name == "Replace mold set"
    assert "No direct sensor data" in detail.ai_recommendation


def test_component_with_sensor_data_returns_sensor_summary() -> None:
    detail = get_component_detail(3, 304)

    assert detail.component.component_name == "Pneumatic System"
    assert detail.component.has_sensor_data is True
    assert detail.sensor_summary is not None
    assert "vibration" in detail.sensor_summary


def test_component_history_is_filtered_by_component() -> None:
    history = get_component_maintenance_history(605)

    assert history
    assert all(item.component_id == 605 for item in history)


def test_component_detail_includes_upcoming_schedule_tasks() -> None:
    detail = get_component_detail(6, 605)

    assert detail.upcoming_tasks
    assert detail.upcoming_tasks[0].task_name == "Replace vacuum suction cups"
    assert detail.upcoming_tasks[0].status == "due_soon"


def test_asset_level_history_and_tasks_are_available() -> None:
    history = get_asset_maintenance_history(3)
    tasks = get_asset_upcoming_tasks(3)

    assert history
    assert tasks
    assert any(item.component_id == 301 for item in history)
    assert any(item.component_id == 301 for item in tasks)


def test_no_sensor_component_does_not_return_fake_sensor_summary() -> None:
    detail = get_component_detail(6, 605)

    assert detail.component.has_sensor_data is False
    assert detail.component.has_cbm is False
    assert detail.sensor_summary is None


def test_component_upcoming_tasks_are_filtered_by_component() -> None:
    tasks = get_component_upcoming_tasks(301)

    assert tasks
    assert all(item.component_id == 301 for item in tasks)


def test_invalid_component_raises_clean_not_found() -> None:
    try:
        get_component_detail(3, 999999)
    except ResourceNotFoundError as exc:
        assert "Component" in exc.message
    else:
        raise AssertionError("Expected ResourceNotFoundError")
