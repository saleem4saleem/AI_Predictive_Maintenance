from app.services.asset_component_service import (
    get_asset_upcoming_tasks,
    get_component_detail,
    get_component_upcoming_tasks,
)


def test_molds_have_visible_upcoming_tasks() -> None:
    tasks = get_component_upcoming_tasks(301)

    assert tasks
    assert tasks[0].task_name == "Replace mold set"


def test_vacuum_suction_cups_have_visible_upcoming_tasks() -> None:
    tasks = get_component_upcoming_tasks(605)

    assert tasks
    assert tasks[0].task_name == "Replace vacuum suction cups"


def test_asset_tasks_aggregate_component_schedule() -> None:
    tasks = get_asset_upcoming_tasks(5)

    task_names = {task.task_name for task in tasks}
    assert "Clean camera lenses" in task_names
    assert "Inspect lighting units" in task_names


def test_component_detail_includes_upcoming_tasks() -> None:
    detail = get_component_detail(1, 103)

    assert detail.upcoming_tasks
    assert detail.upcoming_tasks[0].component_id == 103
