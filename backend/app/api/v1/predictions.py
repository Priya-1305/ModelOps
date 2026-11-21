from fastapi import APIRouter, Request, status, Query
from typing import List, Optional
from backend.app.schemas.prediction import (
    PredictionInput,
    BatchPredictionInput,
    PredictionResponse,
    BatchPredictionResponse,
    PredictionLogItem,
)
from backend.app.services.prediction_service import prediction_service

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def create_prediction(request: PredictionInput, req: Request):
    """
    Generate real-time binary classification prediction for Wisconsin Breast Cancer dataset.
    Extracts or creates correlation ID and logs execution metrics.
    """
    correlation_id = getattr(req.state, "correlation_id", None)
    return prediction_service.predict_single(request, correlation_id=correlation_id)


@router.post("/batch", response_model=BatchPredictionResponse, status_code=status.HTTP_200_OK)
async def create_batch_predictions(request: BatchPredictionInput, req: Request):
    """
    Generate batch classifications with high throughput.
    """
    correlation_id = getattr(req.state, "correlation_id", None)
    return prediction_service.predict_batch(request, correlation_id=correlation_id)


@router.get("", response_model=List[PredictionLogItem], status_code=status.HTTP_200_OK)
async def list_predictions(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    model_version: Optional[str] = Query(default=None),
):
    """
    Retrieve historical prediction logs for auditing and drift monitoring.
    """
    try:
        from backend.app.db.session import SessionLocal
        from backend.app.db.repository import ModelOpsRepository
        with SessionLocal() as db:
            repo = ModelOpsRepository(db)
            logs = repo.list_prediction_logs(model_version=model_version, limit=limit, offset=offset)
            return [
                PredictionLogItem(
                    id=item.id,
                    correlation_id=item.correlation_id,
                    model_name=item.model_name,
                    model_version=item.model_version,
                    prediction=item.prediction,
                    prediction_label=item.prediction_label,
                    probabilities=item.probabilities,
                    latency_ms=item.latency_ms,
                    features=item.features,
                    timestamp=item.timestamp,
                )
                for item in logs
            ]
    except Exception:
        return []
