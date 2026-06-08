from __future__ import annotations

import pytest

from app.ml.model_registry import REQUIRED_METADATA_FIELDS, InvalidModelMetadataError, ModelRegistry


def test_active_model_metadata_can_be_read() -> None:
    metadata = ModelRegistry().load_active_model_metadata()

    assert metadata.model_type == "isolation_forest"
    assert metadata.version == "1.0.0"
    assert metadata.target_type == "anomaly_detection"
    assert metadata.status in {"not_trained", "trained"}


def test_active_model_metadata_has_required_fields() -> None:
    metadata = ModelRegistry().load_active_model_metadata().to_dict()

    assert REQUIRED_METADATA_FIELDS.issubset(metadata.keys())
    assert "vibration" in metadata["features"]
    assert metadata["status"] in {"not_trained", "trained"}


def test_model_registry_status_reports_artifact_availability() -> None:
    status = ModelRegistry().get_status()

    assert status["metadata_available"] is True
    assert "model_file_exists" in status
    assert "scaler_file_exists" in status
    assert status["model_type"] == "isolation_forest"
    assert "model_path" in status
    assert "scaler_path" in status


def test_model_registry_public_status_does_not_expose_paths() -> None:
    status = ModelRegistry().get_public_model_status()

    assert status["model_type"] == "isolation_forest"
    assert status["version"] == "1.0.0"
    assert status["status"] in {"not_trained", "trained"}
    assert "model_path" not in status
    assert "scaler_path" not in status
    assert isinstance(status["model_file_exists"], bool)
    assert isinstance(status["scaler_file_exists"], bool)


def test_model_registry_accessors_return_expected_values() -> None:
    registry = ModelRegistry()

    assert registry.get_model_type() == "isolation_forest"
    assert registry.get_model_version() == "1.0.0"
    assert registry.get_target_type() == "anomaly_detection"
    assert "runtime_hours" in registry.get_feature_columns()
    assert not str(registry.get_active_model_path()).startswith("isolation_forest")


def test_model_registry_validates_missing_required_fields() -> None:
    registry = ModelRegistry()
    valid_metadata = registry.load_active_model_metadata().to_dict()
    valid_metadata.pop("status")

    with pytest.raises(InvalidModelMetadataError):
        registry.validate_metadata(valid_metadata)
