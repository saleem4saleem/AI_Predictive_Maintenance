import pandas as pd

from app.ml.features import DEFAULT_FEATURE_COLUMNS
from app.ml.training_data_builder import (
    build_anomaly_detection_dataset,
    build_failure_classification_dataset_placeholder,
    build_rul_dataset_placeholder,
    load_sample_sensor_data,
)


def test_training_data_builder_loads_sample_sensor_data() -> None:
    data = load_sample_sensor_data()

    assert isinstance(data, pd.DataFrame)
    assert len(data) >= 40
    for column in ["timestamp", "asset_id", "asset_code", *DEFAULT_FEATURE_COLUMNS]:
        assert column in data.columns


def test_training_data_builder_returns_feature_dataset() -> None:
    dataset = build_anomaly_detection_dataset()

    assert list(dataset.columns) == DEFAULT_FEATURE_COLUMNS
    assert dataset.dtypes.apply(lambda dtype: dtype.kind in {"f", "i"}).all()


def test_future_dataset_builders_return_clear_placeholder_status() -> None:
    assert build_failure_classification_dataset_placeholder()["status"] == "not_ready"
    assert build_rul_dataset_placeholder()["status"] == "not_ready"
