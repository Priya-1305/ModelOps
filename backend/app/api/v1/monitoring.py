from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.repository import ModelOpsRepository
from backend.app.services.monitoring_service import monitoring_service
from backend.app.schemas.monitoring import DriftReportResponse

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Drift"])


@router.get("/drift", response_model=DriftReportResponse, status_code=status.HTTP_200_OK)
async def get_drift_report(
    model_name: Optional[str] = Query(default=None),
    threshold: float = Query(default=0.3, ge=0.01, le=1.0),
    db: Session = Depends(get_db),
):
    """
    Run or fetch statistical data drift analysis with Evidently:
    Evaluates covariate shift across all 30 input features.
    Distinguishes data drift from performance degradation.
    """
    return monitoring_service.generate_drift_report(
        model_name=model_name,
        drift_share_threshold=threshold,
        db_session=db,
    )


@router.post("/drift/run", response_model=DriftReportResponse, status_code=status.HTTP_200_OK)
async def trigger_drift_analysis(
    model_name: Optional[str] = Query(default=None),
    threshold: float = Query(default=0.3, ge=0.01, le=1.0),
    db: Session = Depends(get_db),
):
    """Explicitly trigger on-demand data drift evaluation."""
    return monitoring_service.generate_drift_report(
        model_name=model_name,
        drift_share_threshold=threshold,
        db_session=db,
    )


@router.get("/reports", status_code=status.HTTP_200_OK)
async def list_monitoring_reports(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve historical monitoring and drift reports."""
    repo = ModelOpsRepository(db)
    reports = repo.list_monitoring_reports(limit=limit)
    return [
        {
            "id": r.id,
            "model_name": r.model_name,
            "model_version": r.model_version,
            "report_type": r.report_type,
            "data_drift_detected": r.data_drift_detected,
            "prediction_drift_detected": r.prediction_drift_detected,
            "drift_share": r.drift_share,
            "drifted_features_count": r.drifted_features_count,
            "total_features_count": r.total_features_count,
            "summary": r.summary,
            "html_report_path": r.html_report_path,
            "created_at": r.created_at,
        }
        for r in reports
    ]
