from app.contracts.prediction_contract import PredictionContract
from app.services.prediction_orchestrator import run_prediction


def test_prediction_orchestrator_returns_prediction_contract() -> None:
    prediction = run_prediction("3")
    assert isinstance(prediction, PredictionContract)
    assert prediction.asset_code == "IS_MACHINE_001"
    assert prediction.risk_level in {"low", "medium", "high", "critical"}
    assert prediction.explanation
