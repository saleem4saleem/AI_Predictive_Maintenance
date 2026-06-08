from app.services.asset_component_service import (
    get_asset_maintenance_history,
    get_component_detail,
    get_component_maintenance_history,
)


def test_molds_have_visible_past_maintenance_history() -> None:
    history = get_component_maintenance_history(301)

    assert history
    assert any("mold" in (item.failure_description or "").lower() for item in history)


def test_vacuum_suction_cups_have_visible_past_maintenance_history() -> None:
    history = get_component_maintenance_history(605)

    assert history
    assert any("suction" in (item.failure_cause or "").lower() for item in history)


def test_asset_history_aggregates_component_work_orders() -> None:
    history = get_asset_maintenance_history(6)

    assert history
    assert any(item.component_id == 605 for item in history)
    assert any(item.component_id == 606 for item in history)


def test_no_sensor_history_component_stays_strategy_based() -> None:
    detail = get_component_detail(3, 301)

    assert detail.sensor_summary is None
    assert "No direct sensor data" in detail.ai_recommendation
