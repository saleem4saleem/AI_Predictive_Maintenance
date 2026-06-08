from app.contracts.asset_contract import AssetBasicResponse
from app.contracts.asset_detail_contract import AssetDetailResponse
from app.contracts.maintenance_plan_contract import MaintenancePlanResponse
from app.contracts.model_contract import ActiveModelResponse
from app.contracts.overview_contract import OverviewResponse
from app.contracts.prediction_contract import PredictionResponse
from app.contracts.recommendation_contract import RecommendationResponse
from app.services.asset_detail_service import get_asset_detail
from app.services.asset_service import get_asset_by_id, get_assets
from app.services.maintenance_planning_service import get_maintenance_plan
from app.services.model_service import get_active_model
from app.services.overview_service import get_factory_overview
from app.services.prediction_service import get_prediction
from app.services.recommendation_service import get_recommendations


def test_model_service_returns_active_model_contract() -> None:
    model = get_active_model()

    assert isinstance(model, ActiveModelResponse)
    assert model.model_type in {"not_connected_yet", "isolation_forest"}
    assert isinstance(model.features, list)


def test_core_services_return_contract_compatible_objects() -> None:
    overview = get_factory_overview()
    assets = get_assets()
    asset = get_asset_by_id(1)
    detail = get_asset_detail(1)
    prediction = get_prediction(1)
    maintenance_plan = get_maintenance_plan(1)
    recommendations = get_recommendations(1)

    assert isinstance(overview, OverviewResponse)
    assert assets and isinstance(assets[0], AssetBasicResponse)
    assert isinstance(asset, AssetBasicResponse)
    assert isinstance(detail, AssetDetailResponse)
    assert isinstance(prediction, PredictionResponse)
    assert isinstance(maintenance_plan, MaintenancePlanResponse)
    assert isinstance(recommendations, RecommendationResponse)
