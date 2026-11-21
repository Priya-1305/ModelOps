import time
from fastapi import APIRouter, status
from backend.app.config import settings
from backend.app.ml.registry import model_manager
from backend.app.schemas.monitoring import SystemHealthResponse

router = APIRouter(tags=["Health & Readiness"])

APP_START_TIME = time.time()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe to check if service process is alive."""
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness probe to check if model and dependencies are ready to serve inference."""
    is_ready = True
    active_model_name = None
    active_version = None

    try:
        model_entry = model_manager.get_active_model()
        active_model_name = settings.DEFAULT_MODEL_NAME
        active_version = model_entry["metadata"].get("version")
    except Exception:
        # If no model is active yet, not completely ready to serve
        is_ready = False

    uptime = time.time() - APP_START_TIME

    return {
        "status": "READY" if is_ready else "WARMING_UP",
        "ready": is_ready,
        "uptime_seconds": round(uptime, 2),
        "active_model": active_model_name,
        "active_version": active_version,
    }
