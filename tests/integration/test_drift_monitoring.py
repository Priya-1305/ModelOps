import pytest
import pandas as pd
import numpy as np
from backend.app.ml.validation import EXPECTED_FEATURE_NAMES
from backend.app.services.monitoring_service import monitoring_service


def test_drift_report_endpoint(client):
    response = client.get("/api/v1/monitoring/drift")
    assert response.status_code == 200
    data = response.json()
    assert "data_drift_detected" in data
    assert "prediction_drift_detected" in data
    assert "drift_share" in data
    assert "feature_details" in data
    assert len(data["feature_details"]) == 30
    assert "methodological_note" in data["summary"]
    # Check that report makes the methodological distinction
    assert "does not intrinsically imply" in data["summary"]["methodological_note"]


def test_drift_detection_with_synthetic_covariate_shift():
    """Verify that severe covariate shift is properly identified by statistical tests."""
    from backend.app.ml.dataset import prepare_dataset_splits
    splits = prepare_dataset_splits()
    
    # Artificially shift half the features by adding 5 standard deviations
    shifted_data = splits.X_val.copy()
    for col in EXPECTED_FEATURE_NAMES[:15]:
        shifted_data[col] = shifted_data[col] + 1000.0

    report = monitoring_service.generate_drift_report(
        model_name="breast_cancer_classifier",
        current_data=shifted_data,
        drift_share_threshold=0.25,
    )

    assert report.data_drift_detected is True
    assert report.drifted_features_count >= 10
    assert report.drift_share >= 0.25


def test_retraining_trigger_workflow(client):
    payload = {
        "reason": "Feature drift threshold exceeded on 12 features",
        "model_name": "breast_cancer_classifier",
        "model_type": "random_forest",
        "hyperparameters": {"n_estimators": 25, "max_depth": 4, "random_state": 42},
    }
    response = client.post("/api/v1/retraining/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "candidate_version" in data
    assert "recommendation" in data
    assert data["recommendation"] in ["RECOMMENDED_FOR_PROMOTION", "REJECTED_BELOW_PRODUCTION"]
    assert "decision_rationale" in data
    assert "metric_deltas" in data
    assert "delta_f1_score" in data["metric_deltas"]
    assert "promotion_instructions" in data
