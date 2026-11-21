from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class TrainingRunCreate(BaseModel):
    model_name: str = Field(default="breast_cancer_classifier")
    model_type: str = Field(default="logistic_regression", description="'logistic_regression' or 'random_forest'")
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    experiment_name: Optional[str] = Field(default="breast_cancer_wisconsin")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict)
    auto_register: bool = Field(default=True, description="Automatically register trained model in registry as candidate")


class TrainingRunResponse(BaseModel):
    id: str
    run_name: str
    experiment_id: str
    status: str
    model_type: str
    version: Optional[str] = None
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    dataset_metadata: Dict[str, Any]
    artifact_uri: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    registered_version_id: Optional[str] = None


class ExperimentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    run_count: int = 0
    runs: List[TrainingRunResponse] = []
