from __future__ import annotations

from app.ml.base_model import BaseMaintenanceModel
from app.ml.model_registry import ModelRegistry
from app.ml.pipelines.autoencoder_pipeline import AutoencoderMaintenanceModel
from app.ml.pipelines.isolation_forest_pipeline import IsolationForestMaintenanceModel
from app.ml.pipelines.lstm_rul_pipeline import LstmRulMaintenanceModel
from app.ml.pipelines.random_forest_pipeline import RandomForestMaintenanceModel
from app.ml.pipelines.xgboost_pipeline import XGBoostMaintenanceModel

SUPPORTED_MODEL_TYPES = {
    "isolation_forest": IsolationForestMaintenanceModel,
    "random_forest": RandomForestMaintenanceModel,
    "xgboost": XGBoostMaintenanceModel,
    "autoencoder": AutoencoderMaintenanceModel,
    "lstm_rul": LstmRulMaintenanceModel,
}

FUTURE_MODEL_TYPES = {"random_forest", "xgboost", "autoencoder", "lstm_rul"}


class ModelFactoryError(RuntimeError):
    """Raised when the backend cannot construct the requested model safely."""


class ModelFactory:
    """Loads the active model behind a stable backend interface."""

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()

    def load_active_model(self) -> BaseMaintenanceModel:
        metadata = self.registry.load_active_metadata()
        model_class = SUPPORTED_MODEL_TYPES.get(metadata.model_type)
        if model_class is None:
            raise ModelFactoryError(f"Unsupported model type: {metadata.model_type}")

        if metadata.model_type != "isolation_forest":
            raise ModelFactoryError(
                f"Model type '{metadata.model_type}' is recognized but not implemented yet."
            )

        model_path = self.registry.get_active_model_path()
        scaler_path = self.registry.get_scaler_path()
        if not model_path.exists() or not scaler_path.exists():
            raise ModelFactoryError(
                "Active model artifacts are missing. Run 'python -m app.ml.train' first."
            )

        return model_class.load(model_path, scaler_path=scaler_path, metadata=metadata.to_dict())


def get_model(model_type: str) -> type[BaseMaintenanceModel]:
    model_class = SUPPORTED_MODEL_TYPES.get(model_type)
    if model_class is None:
        raise ModelFactoryError(f"Unsupported model type: {model_type}")
    return model_class


def get_active_model() -> BaseMaintenanceModel:
    return ModelFactory().load_active_model()
