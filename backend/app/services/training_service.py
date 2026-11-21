import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.core.logging import logger
from backend.app.ml.dataset import prepare_dataset_splits
from backend.app.ml.pipeline import build_pipeline
from backend.app.ml.evaluator import evaluate_model_performance
from backend.app.ml.tracking import MLflowTracker
from backend.app.ml.registry import model_manager
from backend.app.schemas.training import TrainingRunCreate
from backend.app.db.session import SessionLocal
from backend.app.db.repository import ModelOpsRepository


class TrainingService:
    def __init__(self):
        self.tracker = MLflowTracker()

    def train_model(self, run_input: TrainingRunCreate) -> Dict[str, Any]:
        """
        Executes end-to-end ML training run:
        1. Ingests & validates dataset with stratified train/val/test splits (no data leakage).
        2. Builds and fits preprocessing + model pipeline.
        3. Evaluates candidate on validation split and held-out test split.
        4. Logs metrics, hyperparameters, and artifacts to MLflow.
        5. Saves model artifact to model registry store.
        6. Persists metadata to database repository.
        """
        start_time = time.perf_counter()
        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)

        logger.info(f"Starting training run {run_id} for model '{run_input.model_name}' (type: {run_input.model_type})")

        # 1. Dataset splits (train: 70%, val: 15%, test: 15%)
        splits = prepare_dataset_splits(test_size=0.15, val_size=0.15, random_state=42)

        # 2. Build Pipeline (StandardScaler + Classifier inside pipeline prevents leakage)
        pipeline = build_pipeline(
            model_type=run_input.model_type,  # type: ignore
            hyperparameters=run_input.hyperparameters
        )

        # 3. Fit pipeline on training data
        pipeline.fit(splits.X_train, splits.y_train)

        # 4. Evaluate on validation split (for model tuning and candidate evaluation)
        val_metrics = evaluate_model_performance(pipeline, splits.X_val, splits.y_val, splits.target_names)

        # 5. Evaluate on held-out test split (strictly for final benchmark, not for selection)
        test_metrics = evaluate_model_performance(pipeline, splits.X_test, splits.y_test, splits.target_names)

        combined_metrics = {
            "val_accuracy": val_metrics["accuracy"],
            "val_precision": val_metrics["precision"],
            "val_recall": val_metrics["recall"],
            "val_f1_score": val_metrics["f1_score"],
            "val_roc_auc": val_metrics["roc_auc"],
            "test_accuracy": test_metrics["accuracy"],
            "test_precision": test_metrics["precision"],
            "test_recall": test_metrics["recall"],
            "test_f1_score": test_metrics["f1_score"],
            "test_roc_auc": test_metrics["roc_auc"],
            "val_confusion_matrix": val_metrics["confusion_matrix"],
            "test_confusion_matrix": test_metrics["confusion_matrix"],
        }

        # 6. MLflow Tracking
        mlflow_res = self.tracker.log_training_run(
            run_name=f"{run_input.model_name}_{run_input.model_type}_{run_id[:8]}",
            model_type=run_input.model_type,
            hyperparameters=run_input.hyperparameters or {},
            metrics={k: v for k, v in combined_metrics.items() if isinstance(v, (int, float))},
            tags={**run_input.tags, "run_id": run_id},
            model=pipeline,
            artifacts={
                "validation_evaluation.json": val_metrics,
                "test_evaluation.json": test_metrics,
                "dataset_metadata.json": splits.metadata,
            }
        )

        duration = time.perf_counter() - start_time
        completed_at = datetime.now(timezone.utc)

        # 7. Model Registry persistence if auto_register
        version_number = f"1.{int(time.time()) % 10000}"
        artifact_path = None
        if run_input.auto_register:
            model_metadata = {
                "training_run_id": run_id,
                "model_type": run_input.model_type,
                "hyperparameters": run_input.hyperparameters,
                "metrics": combined_metrics,
                "dataset_metadata": splits.metadata,
                "mlflow_run_id": mlflow_res.get("run_id"),
                "stage": "candidate",
            }
            artifact_path = str(model_manager.save_model_artifact(
                model=pipeline,
                model_name=run_input.model_name,
                version=version_number,
                metadata=model_metadata
            ))

        # 8. Database Persistence
        try:
            with SessionLocal() as db:
                repo = ModelOpsRepository(db)
                exp = repo.get_or_create_experiment(
                    name=run_input.experiment_name or "breast_cancer_wisconsin",
                    description="Experiments and benchmarks on Wisconsin Breast Cancer dataset"
                )
                db_run = repo.create_training_run({
                    "id": run_id,
                    "experiment_id": exp.id,
                    "run_name": f"{run_input.model_name}_{run_input.model_type}_{run_id[:8]}",
                    "status": "COMPLETED",
                    "model_type": run_input.model_type,
                    "parameters": run_input.hyperparameters or {},
                    "metrics": combined_metrics,
                    "dataset_metadata": splits.metadata,
                    "artifact_uri": artifact_path or mlflow_res.get("artifact_uri"),
                    "mlflow_run_id": mlflow_res.get("run_id"),
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "duration_seconds": round(duration, 3),
                })

                if run_input.auto_register:
                    reg_model = repo.get_or_create_registered_model(run_input.model_name)
                    repo.create_model_version({
                        "id": str(uuid.uuid4()),
                        "registered_model_id": reg_model.id,
                        "version_number": version_number,
                        "training_run_id": run_id,
                        "stage": "candidate",
                        "metrics": combined_metrics,
                        "parameters": run_input.hyperparameters,
                        "artifact_uri": artifact_path or "",
                        "description": f"Candidate model from run {run_id[:8]} ({run_input.model_type})",
                        "created_at": completed_at,
                    })
        except Exception as ex:
            logger.warning(f"Database persistence skipped or failed during training run: {ex}")

        return {
            "id": run_id,
            "run_name": f"{run_input.model_name}_{run_input.model_type}_{run_id[:8]}",
            "experiment_id": mlflow_res.get("experiment_id", "default"),
            "status": "COMPLETED",
            "model_name": run_input.model_name,
            "model_type": run_input.model_type,
            "version": version_number if run_input.auto_register else None,
            "parameters": run_input.hyperparameters or {},
            "metrics": combined_metrics,
            "dataset_metadata": splits.metadata,
            "artifact_uri": artifact_path or mlflow_res.get("artifact_uri"),
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": round(duration, 3),
        }


training_service = TrainingService()
