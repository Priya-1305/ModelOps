from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd


EXPECTED_FEATURE_NAMES = [
    "mean_radius", "mean_texture", "mean_perimeter", "mean_area", "mean_smoothness",
    "mean_compactness", "mean_concavity", "mean_concave_points", "mean_symmetry", "mean_fractal_dimension",
    "radius_error", "texture_error", "perimeter_error", "area_error", "smoothness_error",
    "compactness_error", "concavity_error", "concave_points_error", "symmetry_error", "fractal_dimension_error",
    "worst_radius", "worst_texture", "worst_perimeter", "worst_area", "worst_smoothness",
    "worst_compactness", "worst_concavity", "worst_concave_points", "worst_symmetry", "worst_fractal_dimension"
]


def normalize_feature_keys(features: Dict[str, Any]) -> Dict[str, float]:
    """Normalize dictionary keys to snake_case floats."""
    normalized = {}
    for key, value in features.items():
        norm_key = key.strip().replace(" ", "_")
        try:
            normalized[norm_key] = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Feature '{key}' must be numeric, got: {value}")
    return normalized


def validate_feature_input(features: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates input features for inference:
    1. Check all 30 expected features exist.
    2. Check values are not NaN or Infinite.
    3. Check non-negative constraints where physically meaningful.
    """
    errors: List[str] = []
    normalized = normalize_feature_keys(features)

    # Missing features
    missing = [col for col in EXPECTED_FEATURE_NAMES if col not in normalized]
    if missing:
        errors.append(f"Missing required features: {missing}")

    # Extra/unexpected features check (warning or validation)
    for col in EXPECTED_FEATURE_NAMES:
        if col in normalized:
            val = normalized[col]
            if np.isnan(val) or np.isinf(val):
                errors.append(f"Feature '{col}' cannot be NaN or Inf.")
            if "radius" in col or "perimeter" in col or "area" in col:
                if val <= 0:
                    errors.append(f"Feature '{col}' must be positive, got {val}.")

    is_valid = len(errors) == 0
    return is_valid, errors


def features_dict_to_dataframe(features: Dict[str, Any]) -> pd.DataFrame:
    """Converts a single feature dict into an aligned DataFrame for model inference."""
    normalized = normalize_feature_keys(features)
    is_valid, errors = validate_feature_input(normalized)
    if not is_valid:
        raise ValueError(f"Feature validation failed: {'; '.join(errors)}")
    
    # Return DataFrame with columns strictly in EXPECTED_FEATURE_NAMES order
    row = {col: normalized[col] for col in EXPECTED_FEATURE_NAMES}
    return pd.DataFrame([row], columns=EXPECTED_FEATURE_NAMES)


def batch_features_to_dataframe(features_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """Converts a batch of feature dicts into an aligned DataFrame for batch inference."""
    if not features_list:
        raise ValueError("Batch feature list cannot be empty.")
    
    rows = []
    for idx, item in enumerate(features_list):
        norm = normalize_feature_keys(item)
        is_valid, errors = validate_feature_input(norm)
        if not is_valid:
            raise ValueError(f"Batch item at index {idx} validation failed: {'; '.join(errors)}")
        rows.append({col: norm[col] for col in EXPECTED_FEATURE_NAMES})
    
    return pd.DataFrame(rows, columns=EXPECTED_FEATURE_NAMES)
