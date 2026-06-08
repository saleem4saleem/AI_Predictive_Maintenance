from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_FEATURE_COLUMNS = [
    "vibration",
    "temperature",
    "pressure",
    "current_value",
    "speed",
    "flow",
    "runtime_hours",
]


class FeatureValidationError(ValueError):
    """Raised when backend feature data cannot be used for model prediction."""


def validate_feature_dict(
    features: Mapping[str, Any],
    feature_columns: Iterable[str] | None = None,
) -> dict[str, float]:
    """Validate and normalize a feature dictionary for model input."""
    columns = list(feature_columns or DEFAULT_FEATURE_COLUMNS)
    missing = [column for column in columns if column not in features]
    if missing:
        raise FeatureValidationError(f"Missing required feature(s): {', '.join(missing)}")

    normalized: dict[str, float] = {}
    invalid: list[str] = []
    for column in columns:
        value = features[column]
        try:
            normalized[column] = float(value)
        except (TypeError, ValueError):
            invalid.append(column)

    if invalid:
        raise FeatureValidationError(f"Feature(s) must be numeric: {', '.join(invalid)}")

    return normalized


def feature_dict_to_ordered_list(
    features: Mapping[str, Any],
    feature_columns: Iterable[str] | None = None,
) -> list[float]:
    """Convert a feature dictionary into the stable model feature order."""
    columns = list(feature_columns or DEFAULT_FEATURE_COLUMNS)
    normalized = validate_feature_dict(features, columns)
    return [normalized[column] for column in columns]


def dataframe_to_feature_matrix(
    dataframe: pd.DataFrame,
    feature_columns: Iterable[str] | None = None,
) -> tuple[np.ndarray, list[str]]:
    """Validate a DataFrame and return a numeric feature matrix.

    The returned column list is the stable model feature order. Training code
    uses this so future data sources can be merged before model-specific code
    sees the data.
    """

    columns = list(feature_columns or DEFAULT_FEATURE_COLUMNS)
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise FeatureValidationError(f"Missing required feature column(s): {', '.join(missing)}")

    try:
        matrix = dataframe.loc[:, columns].astype(float).to_numpy()
    except (TypeError, ValueError) as exc:
        raise FeatureValidationError("Feature DataFrame contains non-numeric values.") from exc

    return matrix, columns
