from __future__ import annotations

import pandas as pd

from app.ml.features import DEFAULT_FEATURE_COLUMNS
from app.ml.pipelines.isolation_forest_pipeline import IsolationForestMaintenanceModel


def test_isolation_forest_can_train_and_predict() -> None:
    data = pd.DataFrame(
        [
            [2.0, 70.0, 6.5, 120.0, 100.0, 80.0, 1000.0],
            [2.1, 71.0, 6.4, 122.0, 99.0, 79.0, 1001.0],
            [2.2, 72.0, 6.3, 124.0, 98.0, 78.0, 1002.0],
            [7.2, 96.0, 4.8, 185.0, 74.0, 42.0, 1003.0],
        ],
        columns=DEFAULT_FEATURE_COLUMNS,
    )
    model = IsolationForestMaintenanceModel.train(data)
    prediction = model.predict(
        {
            "vibration": 7.5,
            "temperature": 98.0,
            "pressure": 4.6,
            "current_value": 190.0,
            "speed": 72.0,
            "flow": 40.0,
            "runtime_hours": 1004.0,
        }
    )

    for field in [
        "anomaly_score",
        "is_anomaly",
        "risk_level",
        "confidence",
        "model_type",
        "model_version",
    ]:
        assert field in prediction

    assert prediction["risk_level"] in {"low", "medium", "high", "critical"}
    assert prediction["model_type"] == "isolation_forest"
