from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split


@dataclass
class DatasetSplits:
    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series
    feature_names: List[str]
    target_names: List[str]
    metadata: Dict[str, Any]


def get_feature_names_snake_case(feature_names: List[str]) -> List[str]:
    """Convert raw sklearn feature names (e.g. 'mean radius') to snake_case ('mean_radius')."""
    return [name.replace(" ", "_") for name in feature_names]


def load_raw_dataset() -> Tuple[pd.DataFrame, pd.Series, List[str], List[str]]:
    """
    Loads Wisconsin Breast Cancer dataset as pandas DataFrame and Series.
    Applies standard snake_case column formatting.
    """
    raw_data = load_breast_cancer(as_frame=True)
    df = raw_data.data.copy()
    target = raw_data.target.copy()
    feature_names = list(df.columns)
    snake_case_names = get_feature_names_snake_case(feature_names)
    df.columns = snake_case_names
    target_names = list(raw_data.target_names)
    return df, target, snake_case_names, target_names


def prepare_dataset_splits(
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
) -> DatasetSplits:
    """
    Performs stratified 3-way split (Train / Validation / Test).
    Guarantees no data leakage: split is completed before any preprocessing.
    Validation set is used for candidate model comparison.
    Test set is reserved for final held-out evaluation.
    """
    df, target, feature_names, target_names = load_raw_dataset()

    # First split off the test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        df,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )

    # Next split remaining into train and validation
    adjusted_val_size = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp,
        y_temp,
        test_size=adjusted_val_size,
        random_state=random_state,
        stratify=y_temp,
    )

    metadata = {
        "dataset_name": "breast_cancer_wisconsin",
        "total_samples": len(df),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "num_features": len(feature_names),
        "target_names": target_names,
        "class_distribution_train": y_train.value_counts().to_dict(),
        "class_distribution_test": y_test.value_counts().to_dict(),
        "random_state": random_state,
    }

    return DatasetSplits(
        X_train=X_train,
        X_val=X_val,
        X_test=X_test,
        y_train=y_train,
        y_val=y_val,
        y_test=y_test,
        feature_names=feature_names,
        target_names=target_names,
        metadata=metadata,
    )
