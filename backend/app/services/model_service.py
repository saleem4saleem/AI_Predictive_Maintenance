from __future__ import annotations

from app.contracts.model_contract import ActiveModelResponse
from app.ml.model_registry import ModelRegistry


def get_active_model() -> ActiveModelResponse:
    """Return the public active-model contract.

    This service intentionally hides registry file names and model internals from
    route handlers and frontend clients.
    """

    status = ModelRegistry().get_public_model_status()
    return ActiveModelResponse(
        model_type=str(status.get("model_type", "not_connected_yet")),
        version=str(status.get("version") or status.get("model_version") or "not_connected_yet"),
        status=str(status.get("status", "not_connected_yet")),
        trained_at=status.get("trained_at"),
        features=list(status.get("features") or []),
        component="model",
        ok=bool(status.get("ok", False)),
        detail=str(status.get("detail", "Model status is unavailable.")),
        model_version=str(status.get("model_version") or status.get("version") or "not_connected_yet"),
        target_type=status.get("target_type"),
        model_file_exists=bool(status.get("model_file_exists", False)),
        scaler_file_exists=bool(status.get("scaler_file_exists", False)),
        metrics=status.get("metrics") or {},
    )
