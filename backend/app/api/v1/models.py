from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.services.model_service import model_service
from backend.app.schemas.model import (
    ModelSummaryResponse,
    ModelDetailResponse,
    ModelVersionResponse,
    PromotionRequest,
    RollbackRequest,
)

router = APIRouter(prefix="/models", tags=["Model Registry"])


@router.get("", response_model=List[ModelSummaryResponse], status_code=status.HTTP_200_OK)
async def list_registered_models(db: Session = Depends(get_db)):
    """Retrieve all registered models in the platform."""
    return model_service.list_models(db)


@router.get("/{model_id}", response_model=ModelDetailResponse, status_code=status.HTTP_200_OK)
async def get_model_details(model_id: str, db: Session = Depends(get_db)):
    """Get metadata and version history for a specific registered model."""
    return model_service.get_model_details(model_id, db)


@router.get("/{model_id}/versions", response_model=List[ModelVersionResponse], status_code=status.HTTP_200_OK)
async def get_model_versions(model_id: str, db: Session = Depends(get_db)):
    """List all deployed and candidate versions of a model."""
    return model_service.get_model_versions(model_id, db)


@router.post("/{model_id}/versions/{version}/promote", response_model=ModelVersionResponse, status_code=status.HTTP_200_OK)
async def promote_model_version(
    model_id: str,
    version: str,
    request: PromotionRequest,
    db: Session = Depends(get_db),
):
    """
    Controlled promotion gate:
    Evaluates candidate metrics against validation criteria and promotes model to production.
    Never silently replaces production models.
    """
    return model_service.promote_model_version(model_id, version, request, db)


@router.post("/{model_id}/rollback", response_model=ModelVersionResponse, status_code=status.HTTP_200_OK)
async def rollback_model(
    model_id: str,
    request: RollbackRequest,
    db: Session = Depends(get_db),
):
    """
    Rollback production model to previous stable version.
    """
    return model_service.rollback_model(model_id, request, db)
