import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.core.logging import logger
from backend.app.schemas.training import TrainingRunCreate
from backend.app.services.training_service import training_service
from backend.app.services.model_service import model_service
from backend.app.db.session import SessionLocal
from backend.app.db.repository import ModelOpsRepository


class RetrainingService:
    def trigger_retraining(
        self,
        reason: str = "Drift detection triggered retraining",
        model_name: str = "breast_cancer_classifier",
        model_type: str = "random_forest",
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Controlled retraining workflow:
        1. Identifies triggering event.
        2. Trains new candidate model.
        3. Evaluates against defined validation criteria.
        4. Compares with current production model.
        5. Generates comparison report and recommendation.
        6. DOES NOT silently promote. Promotion requires explicit approval.
        """
        logger.info(f"Initiating controlled retraining workflow for '{model_name}'. Reason: {reason}")
        started_at = datetime.now(timezone.utc)

        # 1. Train candidate model
        run_input = TrainingRunCreate(
            model_name=model_name,
            model_type=model_type,
            hyperparameters=hyperparameters or {"n_estimators": 50, "max_depth": 5, "random_state": int(time.time()) % 1000},
            experiment_name="automated_retraining",
            tags={"trigger_reason": reason, "workflow": "retraining"},
            auto_register=True,
        )
        candidate_run = training_service.train_model(run_input)
        candidate_version = candidate_run.get("version")

        # 2. Retrieve current production model metrics for comparison
        prod_metrics = {}
        prod_version = None
        with SessionLocal() as db:
            repo = ModelOpsRepository(db)
            current_prod = repo.get_active_production_version(model_name)
            if current_prod:
                prod_version = current_prod.version_number
                prod_metrics = current_prod.metrics or {}

        # 3. Compare candidate vs production
        candidate_metrics = candidate_run.get("metrics", {})
        cand_f1 = candidate_metrics.get("val_f1_score", 0.0)
        cand_auc = candidate_metrics.get("val_roc_auc", 0.0)
        cand_acc = candidate_metrics.get("val_accuracy", 0.0)

        prod_f1 = prod_metrics.get("val_f1_score", 0.90)
        prod_auc = prod_metrics.get("val_roc_auc", 0.90)
        prod_acc = prod_metrics.get("val_accuracy", 0.90)

        delta_f1 = round(cand_f1 - prod_f1, 4)
        delta_auc = round(cand_auc - prod_auc, 4)
        delta_acc = round(cand_acc - prod_acc, 4)

        # 4. Evaluation Recommendation Gate
        is_f1_acceptable = cand_f1 >= 0.88
        is_auc_acceptable = cand_auc >= 0.88
        outperforms_prod = (delta_f1 >= -0.02) and (delta_auc >= -0.02)

        if is_f1_acceptable and is_auc_acceptable and outperforms_prod:
            recommendation = "RECOMMENDED_FOR_PROMOTION"
            decision_rationale = (
                f"Candidate model (v{candidate_version}) satisfies validation criteria: "
                f"Val F1={cand_f1:.4f} (Δ={delta_f1:+.4f}), Val ROC-AUC={cand_auc:.4f} (Δ={delta_auc:+.4f})."
            )
        else:
            recommendation = "REJECTED_BELOW_PRODUCTION"
            decision_rationale = (
                f"Candidate model (v{candidate_version}) did not pass promotion gate: "
                f"Val F1={cand_f1:.4f} vs Prod {prod_f1:.4f}, Val ROC-AUC={cand_auc:.4f} vs Prod {prod_auc:.4f}."
            )

        logger.info(f"Retraining assessment completed: {recommendation}. {decision_rationale}")

        return {
            "retraining_id": str(uuid.uuid4()),
            "model_name": model_name,
            "trigger_reason": reason,
            "candidate_version": candidate_version,
            "candidate_run_id": candidate_run.get("id"),
            "current_production_version": prod_version,
            "candidate_metrics": candidate_metrics,
            "production_metrics": prod_metrics,
            "metric_deltas": {
                "delta_f1_score": delta_f1,
                "delta_roc_auc": delta_auc,
                "delta_accuracy": delta_acc,
            },
            "recommendation": recommendation,
            "decision_rationale": decision_rationale,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc),
            "promotion_instructions": (
                f"To promote this candidate to production, submit a POST request to: "
                f"/api/v1/models/{model_name}/versions/{candidate_version}/promote"
            ),
        }


retraining_service = RetrainingService()
