from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.repository import ModelOpsRepository
from backend.app.services.training_service import training_service
from backend.app.schemas.training import TrainingRunCreate, TrainingRunResponse
from backend.app.core.exceptions import ModelOpsException

router = APIRouter(prefix="/training-runs", tags=["Training Pipeline"])


@router.post("", response_model=TrainingRunResponse, status_code=status.HTTP_201_CREATED)
async def create_training_run(run_input: TrainingRunCreate):
    """
    Trigger an automated training run:
    Executes dataset splitting, preprocessing pipeline, model training, evaluation,
    MLflow tracking, and model registration.
    """
    result = training_service.train_model(run_input)
    return result


@router.get("", response_model=List[TrainingRunResponse], status_code=status.HTTP_200_OK)
async def list_training_runs(
    experiment_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List historical training runs with hyperparameters and evaluation metrics."""
    repo = ModelOpsRepository(db)
    runs = repo.list_training_runs(experiment_id=experiment_id, limit=limit, offset=offset)
    return [
        TrainingRunResponse(
            id=r.id,
            run_name=r.run_name,
            experiment_id=r.experiment_id,
            status=r.status,
            model_type=r.model_type,
            parameters=r.parameters,
            metrics=r.metrics,
            dataset_metadata=r.dataset_metadata,
            artifact_uri=r.artifact_uri,
            started_at=r.started_at,
            completed_at=r.completed_at,
            duration_seconds=r.duration_seconds,
        )
        for r in runs
    ]


@router.get("/{run_id}", response_model=TrainingRunResponse, status_code=status.HTTP_200_OK)
async def get_training_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve full details, metrics, and dataset metadata for a specific training run."""
    repo = ModelOpsRepository(db)
    r = repo.get_training_run(run_id)
    if not r:
        raise ModelOpsException(f"Training run '{run_id}' not found.", status_code=404)

    return TrainingRunResponse(
        id=r.id,
        run_name=r.run_name,
        experiment_id=r.experiment_id,
        status=r.status,
        model_type=r.model_type,
        parameters=r.parameters,
        metrics=r.metrics,
        dataset_metadata=r.dataset_metadata,
        artifact_uri=r.artifact_uri,
        started_at=r.started_at,
        completed_at=r.completed_at,
        duration_seconds=r.duration_seconds,
    )
