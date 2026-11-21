from typing import Dict, Any, Literal
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

ModelType = Literal["logistic_regression", "random_forest"]


def build_pipeline(model_type: ModelType = "logistic_regression", hyperparameters: Dict[str, Any] = None) -> Pipeline:
    """
    Builds an end-to-end scikit-learn Pipeline.
    Preprocessing (StandardScaler) is strictly encapsulated inside the pipeline
    to prevent data leakage across train, validation, and test splits.
    """
    hyperparameters = hyperparameters or {}

    if model_type == "logistic_regression":
        defaults = {
            "C": 1.0,
            "max_iter": 1000,
            "random_state": 42,
            "solver": "lbfgs"
        }
        params = {**defaults, **hyperparameters}
        classifier = LogisticRegression(**params)

    elif model_type == "random_forest":
        defaults = {
            "n_estimators": 100,
            "max_depth": 5,
            "min_samples_split": 2,
            "random_state": 42
        }
        params = {**defaults, **hyperparameters}
        classifier = RandomForestClassifier(**params)

    else:
        raise ValueError(f"Unsupported model type: {model_type}. Supported: 'logistic_regression', 'random_forest'.")

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", classifier),
        ]
    )
    return pipeline
