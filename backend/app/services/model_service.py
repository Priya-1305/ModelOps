from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.metrics import ACTIVE_MODEL_VERSION
from backend.app.core.exceptions import (
    ModelNotFoundException,
    PromotionRejectedException,
)
from backend.app.db.repository import ModelOpsRepository
from backend.app.db.models import RegisteredModel, ModelVersion, Deployment
from backend.app.ml.registry import model_manager
from backend.app.schemas.model import (
    ModelSummaryResponse,
    ModelDetailResponse,
    ModelVersionResponse,
    PromotionRequest,
    RollbackRequest,
)


class ModelService:
    def list_models(self, db: Session) -> List[ModelSummaryResponse]:
        repo = ModelOpsRepository(db)
        models = repo.list_registered_models()
        summaries = []
        for m in models:
            active_ver = repo.get_active_production_version(m.name)
            summaries.append(
                ModelSummaryResponse(
                    id=m.id,
                    name=m.name,
                    description=m.description,
                    active_version=active_ver.version_number if active_ver else None,
                    version_count=len(m.versions),
                    created_at=m.created_at,
                    updated_at=m.updated_at,
                )
            )
        return summaries

    def get_model_details(self, model_id_or_name: str, db: Session) -> ModelDetailResponse:
        repo = ModelOpsRepository(db)
        model = repo.get_registered_model_by_id_or_name(model_id_or_name)
        if not model:
            raise ModelNotFoundException(f"Registered model '{model_id_or_name}' not found.")

        active_ver = repo.get_active_production_version(model.name)
        versions_resp = [
            ModelVersionResponse(
                id=v.id,
                model_name=model.name,
                version=v.version_number,
                stage=v.stage,
                metrics=v.metrics,
                parameters=v.parameters,
                artifact_uri=v.artifact_uri,
                training_run_id=v.training_run_id,
                description=v.description,
                created_at=v.created_at,
                promoted_at=v.promoted_at,
            )
            for v in model.versions
        ]

        return ModelDetailResponse(
            id=model.id,
            name=model.name,
            description=model.description,
            active_version=active_ver.version_number if active_ver else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
            versions=versions_resp,
        )

    def get_model_versions(self, model_id_or_name: str, db: Session) -> List[ModelVersionResponse]:
        repo = ModelOpsRepository(db)
        versions = repo.list_model_versions(model_id_or_name)
        results = []
        for v in versions:
            results.append(
                ModelVersionResponse(
                    id=v.id,
                    model_name=v.registered_model.name if v.registered_model else model_id_or_name,
                    version=v.version_number,
                    stage=v.stage,
                    metrics=v.metrics,
                    parameters=v.parameters,
                    artifact_uri=v.artifact_uri,
                    training_run_id=v.training_run_id,
                    description=v.description,
                    created_at=v.created_at,
                    promoted_at=v.promoted_at,
                )
            )
        return results

    def promote_model_version(
        self,
        model_id_or_name: str,
        version_number: str,
        request: PromotionRequest,
        db: Session,
    ) -> ModelVersionResponse:
        """
        Controlled promotion workflow:
        1. Validates candidate model exists.
        2. Evaluates acceptance criteria (F1 score & ROC-AUC gates).
        3. Never silently replaces production: archives previous production version explicitly.
        4. Activates candidate in in-memory serving cache.
        5. Updates Prometheus metric gauge.
        6. Logs deployment audit trail.
        """
        repo = ModelOpsRepository(db)
        target_version = repo.get_model_version(model_id_or_name, version_number)
        if not target_version:
            raise ModelNotFoundException(f"Version '{version_number}' of model '{model_id_or_name}' not found.")

        model_name = target_version.registered_model.name

        # Quality Gate Verification
        if not request.force:
            metrics = target_version.metrics or {}
            f1 = metrics.get("val_f1_score", metrics.get("f1_score", 0.0))
            roc_auc = metrics.get("val_roc_auc", metrics.get("roc_auc", 0.0))

            errors = []
            if request.minimum_f1_score and f1 < request.minimum_f1_score:
                errors.append(f"F1 score {f1:.4f} is below minimum requirement of {request.minimum_f1_score:.4f}")
            if request.minimum_roc_auc and roc_auc < request.minimum_roc_auc:
                errors.append(f"ROC-AUC {roc_auc:.4f} is below minimum requirement of {request.minimum_roc_auc:.4f}")

            if errors:
                raise PromotionRejectedException(
                    f"Candidate model rejected by automated quality gate: {'; '.join(errors)}"
                )

        now = datetime.now(timezone.utc)

        # Archive current production models for this registered model
        current_prod = repo.get_active_production_version(model_name)
        if current_prod and current_prod.id != target_version.id:
            current_prod.stage = "archived"
            logger.info(f"Demoted model '{model_name}' version '{current_prod.version_number}' to 'archived'.")

        # Promote target version
        target_version.stage = request.target_stage
        target_version.promoted_at = now

        # Record deployment
        deployment = repo.create_deployment({
            "model_version_id": target_version.id,
            "environment": "production" if request.target_stage == "production" else "staging",
            "status": "active",
            "deployed_at": now,
            "deployed_by": "modelops_gatekeeper",
            "config": {
                "promotion_reason": request.comment or "Automated quality gate passed",
                "forced": request.force,
            }
        })

        db.commit()
        db.refresh(target_version)

        # Warm in-memory cache and update Prometheus gauge
        if request.target_stage == "production":
            model_manager.set_active_version(model_name, version_number)
            ACTIVE_MODEL_VERSION.labels(model_name=model_name, version=version_number).set(1)

        logger.info(f"Model '{model_name}' version '{version_number}' successfully promoted to '{request.target_stage}'.")

        return ModelVersionResponse(
            id=target_version.id,
            model_name=model_name,
            version=target_version.version_number,
            stage=target_version.stage,
            metrics=target_version.metrics,
            parameters=target_version.parameters,
            artifact_uri=target_version.artifact_uri,
            training_run_id=target_version.training_run_id,
            description=target_version.description,
            created_at=target_version.created_at,
            promoted_at=target_version.promoted_at,
        )

    def rollback_model(
        self,
        model_id_or_name: str,
        request: RollbackRequest,
        db: Session,
    ) -> ModelVersionResponse:
        """
        Controlled rollback workflow:
        1. Identifies previous stable version to restore.
        2. Demotes current production model to archived.
        3. Restores target rollback version to production.
        4. Records rollback event in deployments log.
        5. Updates in-memory active serving instance.
        """
        repo = ModelOpsRepository(db)
        model = repo.get_registered_model_by_id_or_name(model_id_or_name)
        if not model:
            raise ModelNotFoundException(f"Registered model '{model_id_or_name}' not found.")

        current_prod = repo.get_active_production_version(model.name)

        target_version: Optional[ModelVersion] = None
        if request.target_version:
            target_version = repo.get_model_version(model.name, request.target_version)
            if not target_version:
                raise ModelNotFoundException(f"Target rollback version '{request.target_version}' not found.")
        else:
            # Pick latest archived or previously promoted version
            all_versions = repo.list_model_versions(model.name)
            candidates = [v for v in all_versions if v.stage in ("archived", "candidate") and (not current_prod or v.id != current_prod.id)]
            if not candidates:
                raise PromotionRejectedException("No previous stable model version available to rollback to.")
            target_version = candidates[0]

        now = datetime.now(timezone.utc)

        # Demote current
        if current_prod:
            current_prod.stage = "rolled_back"

        # Restore target
        target_version.stage = "production"
        target_version.promoted_at = now

        # Create rollback deployment record
        repo.create_deployment({
            "model_version_id": target_version.id,
            "environment": "production",
            "status": "active",
            "deployed_at": now,
            "deployed_by": "rollback_manager",
            "config": {
                "rollback_reason": request.comment,
                "previous_version": current_prod.version_number if current_prod else None,
            }
        })

        db.commit()
        db.refresh(target_version)

        # Update in-memory serving instance
        model_manager.set_active_version(model.name, target_version.version_number)
        ACTIVE_MODEL_VERSION.labels(model_name=model.name, version=target_version.version_number).set(1)

        logger.info(f"Model '{model.name}' successfully rolled back to version '{target_version.version_number}'.")

        return ModelVersionResponse(
            id=target_version.id,
            model_name=model.name,
            version=target_version.version_number,
            stage=target_version.stage,
            metrics=target_version.metrics,
            parameters=target_version.parameters,
            artifact_uri=target_version.artifact_uri,
            training_run_id=target_version.training_run_id,
            description=target_version.description,
            created_at=target_version.created_at,
            promoted_at=target_version.promoted_at,
        )


model_service = ModelService()
