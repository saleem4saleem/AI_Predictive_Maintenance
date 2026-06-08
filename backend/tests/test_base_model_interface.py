from __future__ import annotations

import pandas as pd
import pytest

from app.ml.base_model import BaseMaintenanceModel
from app.ml.features import DEFAULT_FEATURE_COLUMNS
from app.ml.pipelines.isolation_forest_pipeline import IsolationForestMaintenanceModel


def test_isolation_forest_model_implements_base_interface() -> None:
    assert issubclass(IsolationForestMaintenanceModel, BaseMaintenanceModel)


def test_base_maintenance_model_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseMaintenanceModel()


def test_base_model_methods_exist_on_isolation_forest() -> None:
    data = pd.DataFrame(
        [
            [2.0, 70.0, 6.5, 120.0, 100.0, 80.0, 1000.0],
            [2.1, 71.0, 6.4, 122.0, 99.0, 79.0, 1001.0],
            [7.0, 95.0, 4.8, 180.0, 75.0, 45.0, 1002.0],
        ],
        columns=DEFAULT_FEATURE_COLUMNS,
    )
    model = IsolationForestMaintenanceModel.train(data)

    for method_name in ["train", "predict", "save", "load", "get_model_info"]:
        assert hasattr(model, method_name)
