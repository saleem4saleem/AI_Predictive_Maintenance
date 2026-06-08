def test_asset_detail_includes_component_overview(client) -> None:
    response = client.get("/api/v1/assets/3/detail")

    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert data["components"]

    names = {component["component_name"] for component in data["components"]}
    assert "Molds" in names
    assert "Pneumatic System" in names
    assert data["asset_maintenance_history"]
    assert data["asset_upcoming_tasks"]


def test_packaging_asset_detail_includes_packaging_components(client) -> None:
    response = client.get("/api/v1/assets/6/detail")

    assert response.status_code == 200
    components = response.json()["components"]
    names = {component["component_name"] for component in components}
    assert "Vacuum Suction Cups" in names
    assert "Seal Kit" in names
    assert "Conveyor Belt Alignment" in names
    response_data = response.json()
    assert response_data["asset_maintenance_history"]
    assert response_data["asset_upcoming_tasks"]
