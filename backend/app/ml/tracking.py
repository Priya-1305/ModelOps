import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import mlflow
import mlflow.sklearn
from mlflow.exceptions import MlflowException
from backend.app.config import settings
from backend.app.core.logging import logger

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"


class MLflowTracker:
    """Manages MLflow experiment tracking and artifact logging."""

    def __init__(self, tracking_uri: Optional[str] = None, experiment_name: Optional[str] = None):
        self.tracking_uri = tracking_uri or settings.MLFLOW_TRACKING_URI
        self.experiment_name = experiment_name or settings.MLFLOW_EXPERIMENT_NAME
        self._setup()

    def _setup(self):
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"MLflow initialized with tracking URI: {self.tracking_uri}, experiment: {self.experiment_name}")
        except Exception as e:
            logger.warning(f"Could not connect to configured MLflow URI ({e}). Falling back to local SQLite store.")
            local_db = settings.ARTIFACT_STORE_PATH / "mlflow_fallback.db"
            fallback_uri = f"sqlite:///{str(local_db).replace(os.sep, '/')}"
            mlflow.set_tracking_uri(fallback_uri)
            mlflow.set_experiment(self.experiment_name)

    def log_training_run(
        self,
        run_name: str,
        model_type: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        tags: Optional[Dict[str, str]] = None,
        model: Optional[Any] = None,
        artifacts: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Runs a complete MLflow tracking cycle and logs params, metrics, tags, and model."""
        with mlflow.start_run(run_name=run_name) as run:
            run_id = run.info.run_id
            artifact_uri = run.info.artifact_uri

            # Flatten and log params
            flat_params = {"model_type": model_type}
            for k, v in hyperparameters.items():
                flat_params[f"param_{k}"] = str(v)
            mlflow.log_params(flat_params)

            # Flatten and log scalar metrics
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    mlflow.log_metric(k, float(v))
                elif isinstance(v, dict) and k != "classification_report":
                    for sub_k, sub_v in v.items():
                        if isinstance(sub_v, (int, float)):
                            mlflow.log_metric(f"{k}_{sub_k}", float(sub_v))

            # Set tags
            default_tags = {
                "platform": "ModelOps",
                "framework": "scikit-learn",
                "model_type": model_type,
            }
            if tags:
                default_tags.update(tags)
            mlflow.set_tags(default_tags)

            # Log model
            if model is not None:
                try:
                    mlflow.sklearn.log_model(
                        sk_model=model,
                        artifact_path="model",
                        registered_model_name=None,  # Handled explicitly via Model Registry service
                    )
                except Exception as ex:
                    logger.warning(f"MLflow model logging fallback: {ex}")

            # Log extra artifacts like evaluation reports
            if artifacts:
                temp_dir = settings.ARTIFACT_STORE_PATH / "temp_artifacts" / run_id
                temp_dir.mkdir(parents=True, exist_ok=True)
                for filename, content in artifacts.items():
                    filepath = temp_dir / filename
                    with open(filepath, "w", encoding="utf-8") as f:
                        if isinstance(content, (dict, list)):
                            json.dump(content, f, indent=2)
                        else:
                            f.write(str(content))
                    mlflow.log_artifact(str(filepath))

            logger.info(f"Completed MLflow run: {run_id} ({run_name})")
            return {
                "run_id": run_id,
                "artifact_uri": artifact_uri,
                "experiment_id": run.info.experiment_id,
            }
