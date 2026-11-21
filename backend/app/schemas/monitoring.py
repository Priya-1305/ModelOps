from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FeatureDriftDetail(BaseModel):
    feature_name: str
    drift_detected: bool
    drift_score: float
    stat_test: str
    threshold: float


class DriftReportResponse(BaseModel):
    id: str
    model_name: str
    model_version: str
    generated_at: datetime
    data_drift_detected: bool = Field(..., description="Whether input feature distribution shifted significantly")
    prediction_drift_detected: bool = Field(..., description="Whether model output prediction distribution shifted")
    performance_degradation_detected: Optional[bool] = Field(
        default=None,
        description="Whether ground truth labels reveal real accuracy/F1 decline. Note: Feature drift alone does not prove accuracy degradation."
    )
    drifted_features_count: int
    total_features_count: int
    drift_share: float
    feature_details: List[FeatureDriftDetail] = []
    summary: Dict[str, Any] = {}
    html_report_path: Optional[str] = None


class SystemHealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    uptime_seconds: float
    database_connected: bool
    mlflow_connected: bool
    active_model: Optional[str] = None
    active_version: Optional[str] = None
