from app.contracts.asset_detail_contract import AssetDetailResponse
from app.services.asset_detail_service import get_asset_detail


def test_asset_detail_service_combines_required_sections() -> None:
    detail = get_asset_detail(1)

    assert isinstance(detail, AssetDetailResponse)
    assert detail.asset.asset_id == 1
    assert detail.current_condition.condition
    assert detail.sensor_summary is not None
    assert detail.prediction.asset_id == 1
    assert detail.maintenance_plan.asset_id == 1
    assert detail.recommended_actions
    assert detail.ai_explanation.summary
