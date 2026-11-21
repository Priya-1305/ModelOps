from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ModelVersionResponse(BaseModel):
    id: str
    model_name: str
    version: str
    stage: str = Field(..., description="candidate, staging, production, archived, rejected")
    metrics: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
    artifact_uri: str
    training_run_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    promoted_at: Optional[datetime] = None


class ModelDetailResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    active_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    versions: List[ModelVersionResponse] = []


class ModelSummaryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    active_version: Optional[str] = None
    version_count: int
    created_at: datetime
    updated_at: datetime


class PromotionRequest(BaseModel):
    target_stage: str = Field(default="production", description="Target stage: staging or production")
    minimum_f1_score: Optional[float] = Field(default=0.90, description="Minimum validation F1 score required")
    minimum_roc_auc: Optional[float] = Field(default=0.90, description="Minimum validation ROC-AUC required")
    force: bool = Field(default=False, description="Override automated gate checks if explicitly authorized")
    comment: Optional[str] = Field(default=None, description="Promotion reason / changelog")


class RollbackRequest(BaseModel):
    target_version: Optional[str] = Field(default=None, description="Specific previous version to rollback to. Defaults to previous production version.")
    comment: Optional[str] = Field(default="Manual rollback initiated", description="Rollback reason")
