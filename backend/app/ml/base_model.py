from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Mapping, Sequence, Self


FeatureInput = Mapping[str, float] | Sequence[float]
PredictionOutput = dict[str, Any]


class BaseMaintenanceModel(ABC):
    """Stable interface for every predictive maintenance model.

    API routes and frontend clients must not depend on model-specific details.
    Future models such as Random Forest, XGBoost, Autoencoder, or LSTM RUL
    models should implement this same interface and return the same prediction
    dictionary shape.
    """

    model_type: str
    version: str

    @classmethod
    @abstractmethod
    def train(cls, training_data: Any, **kwargs: Any) -> Self:
        """Train a model from prepared backend training data."""

    @abstractmethod
    def predict(self, features: FeatureInput) -> PredictionOutput:
        """Return a standard prediction dictionary for one feature row."""

    @abstractmethod
    def save(self, path: str | Path, scaler_path: str | Path | None = None) -> None:
        """Persist model artifacts owned by the backend."""

    @classmethod
    @abstractmethod
    def load(
        cls,
        path: str | Path,
        scaler_path: str | Path | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Self:
        """Load model artifacts without exposing paths to the frontend."""

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Return safe model metadata for backend monitoring and debugging."""
