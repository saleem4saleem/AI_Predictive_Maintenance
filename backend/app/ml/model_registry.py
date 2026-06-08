from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import get_settings

REQUIRED_METADATA_FIELDS = {
    "active_model",
    "scaler",
    "model_type",
    "version",
    "trained_at",
    "features",
    "target_type",
    "status",
}


class ModelRegistryError(RuntimeError):
    """Clean model-registry error safe to return through service fallbacks."""


class ActiveModelMetadataMissingError(ModelRegistryError):
    """Raised when active_model.json is missing."""


class InvalidModelMetadataError(ModelRegistryError):
    """Raised when active_model.json is malformed or incomplete."""


@dataclass(frozen=True)
class ActiveModelMetadata:
    active_model: str
    scaler: str
    model_type: str
    version: str
    trained_at: str
    features: list[str]
    target_type: str
    status: str

    @classmethod
    def from_dict(cls, metadata: dict[str, Any]) -> "ActiveModelMetadata":
        cls.validate_metadata(metadata)

        features = metadata["features"]

        return cls(
            active_model=str(metadata["active_model"]),
            scaler=str(metadata["scaler"]),
            model_type=str(metadata["model_type"]),
            version=str(metadata["version"]),
            trained_at=str(metadata["trained_at"]),
            features=features,
            target_type=str(metadata["target_type"]),
            status=str(metadata["status"]),
        )

    @staticmethod
    def validate_metadata(metadata: dict[str, Any]) -> None:
        missing = sorted(REQUIRED_METADATA_FIELDS.difference(metadata))
        if missing:
            raise InvalidModelMetadataError(
                f"active_model.json is missing required field(s): {', '.join(missing)}"
            )

        features = metadata["features"]
        if not isinstance(features, list) or not all(isinstance(item, str) for item in features):
            raise InvalidModelMetadataError("active_model.json field 'features' must be a list of strings.")

        for field in ["active_model", "scaler", "model_type", "version", "trained_at", "target_type", "status"]:
            if not str(metadata[field]).strip():
                raise InvalidModelMetadataError(f"active_model.json field '{field}' cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_model": self.active_model,
            "scaler": self.scaler,
            "model_type": self.model_type,
            "version": self.version,
            "trained_at": self.trained_at,
            "features": self.features,
            "target_type": self.target_type,
            "status": self.status,
        }


class ModelRegistry:
    """Reads active model metadata without exposing model files to the frontend."""

    def __init__(
        self,
        saved_models_dir: str | Path | None = None,
        metadata_file: str | Path | None = None,
    ) -> None:
        settings = get_settings()
        self.saved_models_dir = Path(saved_models_dir or settings.saved_models_dir).resolve()
        self.metadata_file = Path(metadata_file or settings.active_model_metadata_file).resolve()

    def load_active_model_metadata(self) -> ActiveModelMetadata:
        if not self.metadata_file.exists():
            raise ActiveModelMetadataMissingError(
                f"Active model metadata file was not found at {self.metadata_file}."
            )

        try:
            raw_metadata = json.loads(self.metadata_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InvalidModelMetadataError("active_model.json is not valid JSON.") from exc
        except OSError as exc:
            raise ModelRegistryError("active_model.json could not be read.") from exc

        return ActiveModelMetadata.from_dict(raw_metadata)

    def load_active_metadata(self) -> ActiveModelMetadata:
        return self.load_active_model_metadata()

    def get_active_model_path(self) -> Path:
        metadata = self.load_active_metadata()
        return self.saved_models_dir / metadata.active_model

    def get_scaler_path(self) -> Path:
        metadata = self.load_active_metadata()
        return self.saved_models_dir / metadata.scaler

    def get_active_metadata(self) -> ActiveModelMetadata:
        return self.load_active_model_metadata()

    def get_active_model_metadata(self) -> ActiveModelMetadata:
        return self.load_active_model_metadata()

    def get_model_type(self) -> str:
        return self.load_active_model_metadata().model_type

    def get_model_version(self) -> str:
        return self.load_active_model_metadata().version

    def get_feature_list(self) -> list[str]:
        return list(self.load_active_model_metadata().features)

    def get_feature_columns(self) -> list[str]:
        return self.get_feature_list()

    def get_target_type(self) -> str:
        return self.load_active_model_metadata().target_type

    def model_file_exists(self) -> bool:
        return self.get_active_model_path().exists()

    def scaler_file_exists(self) -> bool:
        return self.get_scaler_path().exists()

    def validate_metadata(self, metadata: dict[str, Any] | None = None) -> None:
        if metadata is None:
            self.load_active_model_metadata()
            return
        ActiveModelMetadata.validate_metadata(metadata)

    def get_model_status(self, *, include_paths: bool = True) -> dict[str, Any]:
        try:
            metadata = self.load_active_model_metadata()
        except ModelRegistryError as exc:
            return {
                "component": "model",
                "ok": False,
                "status": "unavailable",
                "metadata_available": False,
                "model_file_exists": False,
                "scaler_file_exists": False,
                "detail": str(exc),
            }

        model_path = self.saved_models_dir / metadata.active_model
        scaler_path = self.saved_models_dir / metadata.scaler
        model_exists = model_path.exists()
        scaler_exists = scaler_path.exists()
        artifacts_exist = model_exists and scaler_exists
        status = {
            "component": "model",
            "ok": artifacts_exist,
            "status": metadata.status,
            "metadata_available": True,
            "model_file_exists": model_exists,
            "scaler_file_exists": scaler_exists,
            "detail": _status_detail(metadata.status, artifacts_exist),
            "model_type": metadata.model_type,
            "version": metadata.version,
            "model_version": metadata.version,
            "trained_at": metadata.trained_at,
            "features": metadata.features,
            "target_type": metadata.target_type,
        }
        if include_paths:
            status["model_path"] = str(model_path)
            status["scaler_path"] = str(scaler_path)
        return status

    def get_status(self) -> dict[str, Any]:
        return self.get_model_status(include_paths=True)

    def get_public_model_status(self) -> dict[str, Any]:
        status = self.get_model_status(include_paths=False)
        return {
            "model_type": status.get("model_type", "unavailable"),
            "version": status.get("version", "unavailable"),
            "status": status.get("status", "unavailable"),
            "trained_at": status.get("trained_at"),
            "features": status.get("features", []),
            "target_type": status.get("target_type"),
            "model_file_exists": bool(status.get("model_file_exists", False)),
            "scaler_file_exists": bool(status.get("scaler_file_exists", False)),
            "component": "model",
            "ok": bool(status.get("ok", False)),
            "detail": status.get("detail"),
            "model_version": status.get("model_version") or status.get("version"),
            "metrics": status.get("metrics"),
        }


def _status_detail(status: str, artifacts_exist: bool) -> str:
    if status == "not_trained":
        return "Active model metadata exists, but the model is marked as not trained."
    if artifacts_exist:
        return "Active model artifacts are available."
    return "Active model metadata exists, but model artifacts are missing."
