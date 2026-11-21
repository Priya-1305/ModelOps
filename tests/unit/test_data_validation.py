import pytest
import numpy as np
from backend.app.ml.validation import (
    validate_feature_input,
    features_dict_to_dataframe,
    EXPECTED_FEATURE_NAMES,
)


def test_validation_success_with_valid_features(valid_features_dict):
    is_valid, errors = validate_feature_input(valid_features_dict)
    assert is_valid is True
    assert len(errors) == 0

    df = features_dict_to_dataframe(valid_features_dict)
    assert df.shape == (1, 30)
    assert list(df.columns) == EXPECTED_FEATURE_NAMES


def test_validation_fails_on_missing_features(valid_features_dict):
    incomplete = valid_features_dict.copy()
    del incomplete["mean_radius"]
    del incomplete["worst_perimeter"]

    is_valid, errors = validate_feature_input(incomplete)
    assert is_valid is False
    assert any("Missing required features" in err for err in errors)


def test_validation_fails_on_nan_values(valid_features_dict):
    corrupted = valid_features_dict.copy()
    corrupted["mean_texture"] = float("nan")

    is_valid, errors = validate_feature_input(corrupted)
    assert is_valid is False
    assert any("cannot be NaN" in err for err in errors)


def test_validation_fails_on_negative_physical_dimension(valid_features_dict):
    invalid = valid_features_dict.copy()
    invalid["mean_radius"] = -5.0

    is_valid, errors = validate_feature_input(invalid)
    assert is_valid is False
    assert any("must be positive" in err for err in errors)
