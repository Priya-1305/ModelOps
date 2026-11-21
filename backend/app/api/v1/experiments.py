from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.repository import ModelOpsRepository
from backend.app.schemas.training import ExperimentResponse, TrainingRunResponse

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.get("", response_model=List[ExperimentResponse], status_code=status.HTTP_200_OK)
async def list_experiments(db: Session = Depends(get_db)):
    """List all tracked ML experiments and their corresponding training runs."""
    repo = ModelOpsRepository(db)
    experiments = repo.list_experiments()
    results = []
    for exp in experiments:
        runs_resp = [
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
            for r in exp.runs
        ]
        results.append(
            ExperimentResponse(
                id=exp.id,
                name=exp.name,
                description=exp.description,
                created_at=exp.created_at,
                run_count=len(exp.runs),
                runs=runs_resp,
            )
        )
    return results
