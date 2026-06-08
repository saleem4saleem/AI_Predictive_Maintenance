import pytest

from app.ml.model_factory import ModelFactoryError, get_model
from app.ml.pipelines.autoencoder_pipeline import AutoencoderMaintenanceModel
from app.ml.pipelines.isolation_forest_pipeline import IsolationForestMaintenanceModel
from app.ml.pipelines.lstm_rul_pipeline import LstmRulMaintenanceModel
from app.ml.pipelines.random_forest_pipeline import RandomForestMaintenanceModel
from app.ml.pipelines.xgboost_pipeline import XGBoostMaintenanceModel


def test_model_factory_returns_isolation_forest_class() -> None:
    assert get_model("isolation_forest") is IsolationForestMaintenanceModel


def test_model_factory_recognizes_future_model_classes() -> None:
    assert get_model("random_forest") is RandomForestMaintenanceModel
    assert get_model("xgboost") is XGBoostMaintenanceModel
    assert get_model("autoencoder") is AutoencoderMaintenanceModel
    assert get_model("lstm_rul") is LstmRulMaintenanceModel


def test_model_factory_rejects_unknown_model_type() -> None:
    with pytest.raises(ModelFactoryError):
        get_model("unsupported_model")
