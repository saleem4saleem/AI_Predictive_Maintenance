import pytest

from app.contracts.asset_contract import AssetBasicResponse
from app.exceptions import ResourceNotFoundError
from app.services.asset_service import get_asset_by_id, get_assets


def test_asset_service_returns_asset_list() -> None:
    assets = get_assets()

    assert len(assets) == 8
    assert isinstance(assets[0], AssetBasicResponse)
    assert assets[0].asset_code == "FURNACE_001"


def test_asset_service_returns_one_asset() -> None:
    asset = get_asset_by_id(1)

    assert asset.asset_id == 1
    assert asset.asset_name == "Furnace"


def test_asset_service_raises_for_missing_asset() -> None:
    with pytest.raises(ResourceNotFoundError):
        get_asset_by_id(999999)
