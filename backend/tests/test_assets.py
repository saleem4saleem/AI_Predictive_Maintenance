from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_assets_endpoint_lists_assets() -> None:
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) == 8
    assert assets[0]["asset_code"] == "FURNACE_001"


def test_asset_endpoint_returns_one_asset() -> None:
    response = client.get("/api/v1/assets/6")
    assert response.status_code == 200
    assert response.json()["asset_code"] == "PACKAGING_001"
