from __future__ import annotations

import pytest
import pandas as pd

from app.ml.features import (
    DEFAULT_FEATURE_COLUMNS,
    FeatureValidationError,
    dataframe_to_feature_matrix,
    feature_dict_to_ordered_list,
    validate_feature_dict,
)


def test_validate_feature_dict_normalizes_numeric_values() -> None:
    features = {column: "1.5" for column in DEFAULT_FEATURE_COLUMNS}

    normalized = validate_feature_dict(features)

    assert set(normalized) == set(DEFAULT_FEATURE_COLUMNS)
    assert all(isinstance(value, float) for value in normalized.values())


def test_feature_dict_to_ordered_list_uses_default_feature_order() -> None:
    features = {column: index for index, column in enumerate(DEFAULT_FEATURE_COLUMNS)}

    ordered = feature_dict_to_ordered_list(features)

    assert ordered == [float(index) for index in range(len(DEFAULT_FEATURE_COLUMNS))]


def test_validate_feature_dict_rejects_missing_feature() -> None:
    features = {column: 1.0 for column in DEFAULT_FEATURE_COLUMNS if column != "flow"}

    with pytest.raises(FeatureValidationError):
        validate_feature_dict(features)


def test_dataframe_to_feature_matrix_returns_stable_order() -> None:
    dataframe = pd.DataFrame([{column: index for index, column in enumerate(DEFAULT_FEATURE_COLUMNS)}])

    matrix, columns = dataframe_to_feature_matrix(dataframe)

    assert columns == DEFAULT_FEATURE_COLUMNS
    assert matrix.shape == (1, len(DEFAULT_FEATURE_COLUMNS))
