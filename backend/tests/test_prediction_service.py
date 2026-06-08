from app.contracts.prediction_contract import PredictionResponse
from app.services.prediction_service import get_prediction, run_prediction


def test_prediction_service_returns_stable_prediction_contract() -> None:
    prediction = get_prediction(1)

    assert isinstance(prediction, PredictionResponse)
    assert prediction.asset_id == 1
    assert prediction.asset_code == "FURNACE_001"
    assert prediction.model_version == "not_connected_yet"


def test_prediction_service_run_prediction_uses_same_contract() -> None:
    prediction = run_prediction(6)

    assert isinstance(prediction, PredictionResponse)
    assert prediction.asset_code == "PACKAGING_001"
