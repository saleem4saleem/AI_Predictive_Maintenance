from app.contracts.overview_contract import OverviewResponse
from app.services.overview_service import get_factory_overview


def test_overview_service_returns_required_dashboard_data() -> None:
    overview = get_factory_overview()

    assert isinstance(overview, OverviewResponse)
    assert overview.factory_name
    assert len(overview.production_flow) == 8
    assert len(overview.assets) == 8
    assert overview.factory_health > 0
