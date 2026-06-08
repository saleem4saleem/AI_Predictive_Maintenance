def test_asset_components_endpoint_returns_is_machine_components(client) -> None:
    response = client.get("/api/v1/assets/3/components")

    assert response.status_code == 200
    data = response.json()
    names = {component["component_name"] for component in data["components"]}
    assert data["asset_id"] == 3
    assert "Molds" in names
    assert "Pneumatic System" in names


def test_component_detail_endpoint_returns_maintenance_history(client) -> None:
    response = client.get("/api/v1/assets/6/components/605")

    assert response.status_code == 200
    data = response.json()
    assert data["component"]["component_name"] == "Vacuum Suction Cups"
    assert data["component"]["has_sensor_data"] is False
    assert data["maintenance_history"]
    assert data["upcoming_tasks"]
    assert data["upcoming_tasks"][0]["task_name"] == "Replace vacuum suction cups"
    assert data["ai_recommendation"]


def test_molds_component_endpoint_has_history_tasks_and_no_sensor_summary(client) -> None:
    response = client.get("/api/v1/assets/3/components/301")

    assert response.status_code == 200
    data = response.json()
    assert data["component"]["component_name"] == "Molds"
    assert data["component"]["has_sensor_data"] is False
    assert data["component"]["has_cbm"] is False
    assert data["sensor_summary"] is None
    assert data["maintenance_history"]
    assert data["upcoming_tasks"]


def test_invalid_component_returns_clean_404(client) -> None:
    response = client.get("/api/v1/assets/3/components/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "resource_not_found"
