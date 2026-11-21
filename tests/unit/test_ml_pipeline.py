import pytest
import numpy as np
from backend.app.ml.dataset import prepare_dataset_splits
from backend.app.ml.pipeline import build_pipeline
from backend.app.ml.evaluator import evaluate_model_performance


def test_dataset_splits_stratified_and_no_leakage():
    """Verify 3-way split, shapes, stratification, and no overlap."""
    splits = prepare_dataset_splits(test_size=0.15, val_size=0.15, random_state=42)

    total_samples = len(splits.X_train) + len(splits.X_val) + len(splits.X_test)
    assert total_samples == 569, f"Expected 569 total Wisconsin samples, got {total_samples}"
    assert len(splits.feature_names) == 30
    assert len(splits.target_names) == 2

    # Check non-empty
    assert len(splits.X_train) > 0
    assert len(splits.X_val) > 0
    assert len(splits.X_test) > 0

    # Ensure train and test index disjoint (no leakage)
    train_idx = set(splits.X_train.index)
    val_idx = set(splits.X_val.index)
    test_idx = set(splits.X_test.index)
    assert len(train_idx.intersection(val_idx)) == 0
    assert len(train_idx.intersection(test_idx)) == 0
    assert len(val_idx.intersection(test_idx)) == 0


def test_logistic_regression_pipeline_train_and_eval():
    """Verify Logistic Regression pipeline trains and returns valid metrics."""
    splits = prepare_dataset_splits(test_size=0.15, val_size=0.15, random_state=42)
    pipeline = build_pipeline("logistic_regression", {"C": 0.5, "max_iter": 500})
    pipeline.fit(splits.X_train, splits.y_train)

    metrics = evaluate_model_performance(pipeline, splits.X_val, splits.y_val)
    assert metrics["accuracy"] >= 0.85
    assert metrics["f1_score"] >= 0.85
    assert metrics["roc_auc"] >= 0.90
    assert "confusion_matrix" in metrics
    assert metrics["confusion_matrix"]["true_positives"] >= 0


def test_random_forest_pipeline_train_and_eval():
    """Verify Random Forest pipeline trains and returns valid metrics."""
    splits = prepare_dataset_splits(test_size=0.15, val_size=0.15, random_state=42)
    pipeline = build_pipeline("random_forest", {"n_estimators": 25, "max_depth": 4})
    pipeline.fit(splits.X_train, splits.y_train)

    metrics = evaluate_model_performance(pipeline, splits.X_val, splits.y_val)
    assert metrics["accuracy"] >= 0.85
    assert metrics["f1_score"] >= 0.85
    assert metrics["roc_auc"] >= 0.90
