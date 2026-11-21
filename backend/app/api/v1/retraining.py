from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, status
from backend.app.services.retraining_service import retraining_service

router = APIRouter(prefix="/retraining", tags=["Automated Retraining"])


class RetrainingTriggerInput(BaseModel):
    reason: str = Field(default="Feature drift detected", description="Reason for triggering retraining run")
    model_name: str = Field(default="breast_cancer_classifier")
    model_type: str = Field(default="random_forest", description="'logistic_regression' or 'random_forest'")
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


@router.post("/trigger", status_code=status.HTTP_200_OK)
async def trigger_retraining(request: RetrainingTriggerInput):
    """
    Controlled retraining workflow:
    1. Trains candidate model on updated or baseline dataset.
    2. Evaluates performance against validation baseline and active production model.
    3. Produces recommendation (RECOMMENDED_FOR_PROMOTION or REJECTED).
    4. Does not automatically deploy: preserves human/gate approval.
    """
    return retraining_service.trigger_retraining(
        reason=request.reason,
        model_name=request.model_name,
        model_type=request.model_type,
        hyperparameters=request.hyperparameters,
    )
