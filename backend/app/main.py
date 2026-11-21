import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import (
    ModelOpsException,
    modelops_exception_handler,
    global_exception_handler,
)
from backend.app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ACTIVE_MODEL_VERSION,
)
from backend.app.ml.registry import model_manager
from backend.app.services.training_service import training_service
from backend.app.schemas.training import TrainingRunCreate
from backend.app.db.session import init_db

# API Routers
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.predictions import router as predictions_router
from backend.app.api.v1.metrics import router as metrics_router
from backend.app.api.v1.models import router as models_router
from backend.app.api.v1.training_runs import router as training_runs_router
from backend.app.api.v1.experiments import router as experiments_router
from backend.app.api.v1.monitoring import router as monitoring_router
from backend.app.api.v1.retraining import router as retraining_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan:
    1. Warm up baseline model in memory during startup.
    2. Register active model version gauge for Prometheus.
    3. Ensure clean shutdown.
    """
    logger.info("Initializing ModelOps platform and warming model cache...")
    try:
        init_db()
    except Exception as db_init_err:
        logger.warning(f"Database initialization warning: {db_init_err}")

    try:
        # Check if an active model already exists on disk
        model_entry = model_manager.get_active_model(settings.DEFAULT_MODEL_NAME)
        logger.info(f"Existing model successfully loaded from registry: {settings.DEFAULT_MODEL_NAME}")
        try:
            with SessionLocal() as db:
                repo = ModelOpsRepository(db)
                reg = repo.get_registered_model_by_id_or_name(settings.DEFAULT_MODEL_NAME)
                if not reg:
                    reg = repo.get_or_create_registered_model(settings.DEFAULT_MODEL_NAME)
                    v_num = model_entry["metadata"].get("version", "1.0")
                    repo.create_model_version({
                        "id": str(uuid.uuid4()),
                        "registered_model_id": reg.id,
                        "version_number": v_num,
                        "stage": "production",
                        "metrics": model_entry["metadata"].get("metrics", {}),
                        "parameters": model_entry["metadata"].get("hyperparameters", {}),
                        "artifact_uri": model_entry["metadata"].get("artifact_path", ""),
                        "promoted_at": datetime.now(timezone.utc),
                    })
        except Exception as sync_err:
            logger.warning(f"Could not sync existing disk model to database: {sync_err}")
    except Exception:
        logger.info("No pre-trained model found on disk. Training initial baseline model...")
        initial_run = TrainingRunCreate(
            model_name=settings.DEFAULT_MODEL_NAME,
            model_type="random_forest",
            hyperparameters={"n_estimators": 50, "max_depth": 5, "random_state": 42},
            experiment_name="baseline_initialization",
            auto_register=True,
        )
        res = training_service.train_model(initial_run)
        if res.get("version"):
            model_manager.set_active_version(settings.DEFAULT_MODEL_NAME, res["version"])
            ACTIVE_MODEL_VERSION.labels(model_name=settings.DEFAULT_MODEL_NAME, version=res["version"]).set(1)
            try:
                from backend.app.db.session import SessionLocal
                from backend.app.db.repository import ModelOpsRepository
                from datetime import datetime, timezone
                with SessionLocal() as db:
                    repo = ModelOpsRepository(db)
                    ver = repo.get_model_version(settings.DEFAULT_MODEL_NAME, res["version"])
                    if ver:
                        ver.stage = "production"
                        ver.promoted_at = datetime.now(timezone.utc)
                        db.commit()
            except Exception as e:
                logger.warning(f"Failed to set initial model stage to production: {e}")
        logger.info(f"Initial baseline model trained and warmed: version {res.get('version')}")

    yield

    logger.info("Shutting down ModelOps platform...")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Production-Grade ML Lifecycle, Deployment, and Monitoring Platform",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Correlation ID & Prometheus HTTP Metrics Middleware
    @app.middleware("http")
    async def metrics_and_correlation_middleware(request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            # Re-raise to let exception handlers capture it
            duration = time.perf_counter() - start_time
            REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code=500).inc()
            REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)
            raise exc

        duration = time.perf_counter() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(duration)

        response.headers["X-Correlation-ID"] = correlation_id
        return response

    # 3. Exception Handlers
    app.add_exception_handler(ModelOpsException, modelops_exception_handler)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Invalid request parameters or payload.",
                    "details": exc.errors(),
                    "correlation_id": correlation_id,
                }
            },
        )

    app.add_exception_handler(Exception, global_exception_handler)

    # 4. Include Routers
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(predictions_router, prefix=settings.API_V1_PREFIX)
    app.include_router(metrics_router, prefix=settings.API_V1_PREFIX)
    app.include_router(models_router, prefix=settings.API_V1_PREFIX)
    app.include_router(training_runs_router, prefix=settings.API_V1_PREFIX)
    app.include_router(experiments_router, prefix=settings.API_V1_PREFIX)
    app.include_router(monitoring_router, prefix=settings.API_V1_PREFIX)
    app.include_router(retraining_router, prefix=settings.API_V1_PREFIX)

    # Prometheus root scraper endpoint
    @app.get("/metrics", include_in_schema=False)
    async def prometheus_metrics():
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app


app = create_application()
