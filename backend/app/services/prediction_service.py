import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import numpy as np
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.metrics import PREDICTION_COUNT, PREDICTION_LATENCY
from backend.app.core.exceptions import InvalidInputException, ModelNotLoadedException
from backend.app.ml.registry import model_manager
from backend.app.ml.validation import (
    features_dict_to_dataframe,
    batch_features_to_dataframe,
    validate_feature_input,
)
from backend.app.schemas.prediction import (
    PredictionInput,
    BatchPredictionInput,
    PredictionResponse,
    BatchPredictionResponse,
)

TARGET_CLASSES = ["malignant", "benign"]


class PredictionService:
    def __init__(self):
        self.registry = model_manager

    def predict_single(
        self,
        request: PredictionInput,
        correlation_id: Optional[str] = None
    ) -> PredictionResponse:
        """
        Executes real-time single inference:
        1. Validates input schema & values.
        2. Retrieves warmed model from in-memory cache (no per-request disk reads).
        3. Generates class prediction and probabilities.
        4. Records latency and logs metrics.
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        model_name = request.model_name or settings.DEFAULT_MODEL_NAME
        
        # 1. Validation
        is_valid, errors = validate_feature_input(request.features)
        if not is_valid:
            PREDICTION_COUNT.labels(model_name=model_name, model_version="unknown", status="validation_error").inc()
            raise InvalidInputException(f"Validation failed: {'; '.join(errors)}")

        # 2. Get loaded model from cache
        model_entry = self.registry.get_model(model_name, request.model_version)
        model = model_entry["model"]
        version = model_entry["metadata"].get("version", "1.0")

        # 3. Format DataFrame
        X = features_dict_to_dataframe(request.features)

        # 4. Run inference with high-resolution timing
        start_time = time.perf_counter()
        try:
            pred_arr = model.predict(X)
            pred_class = int(pred_arr[0])
            pred_label = TARGET_CLASSES[pred_class] if pred_class < len(TARGET_CLASSES) else str(pred_class)

            proba_arr = model.predict_proba(X)[0]
            probabilities = {
                TARGET_CLASSES[i]: round(float(proba_arr[i]), 5)
                for i in range(len(proba_arr))
            }
        except Exception as e:
            PREDICTION_COUNT.labels(model_name=model_name, model_version=version, status="error").inc()
            logger.error(f"Inference execution failed: {e}", extra={"correlation_id": correlation_id})
            raise

        latency_seconds = time.perf_counter() - start_time
        latency_ms = round(latency_seconds * 1000, 3)

        # 5. Prometheus Metrics
        PREDICTION_COUNT.labels(model_name=model_name, model_version=version, status="success").inc()
        PREDICTION_LATENCY.labels(model_name=model_name, model_version=version).observe(latency_seconds)

        # 6. Structured Logging
        logger.info(
            f"Prediction completed: class={pred_class} ({pred_label}), latency={latency_ms}ms",
            extra={
                "correlation_id": correlation_id,
                "model_version": version,
            }
        )

        # 7. Database Persistence
        try:
            from backend.app.db.session import SessionLocal
            from backend.app.db.repository import ModelOpsRepository
            with SessionLocal() as db:
                repo = ModelOpsRepository(db)
                repo.create_prediction_log({
                    "correlation_id": correlation_id,
                    "model_name": model_name,
                    "model_version": version,
                    "features": request.features,
                    "prediction": pred_class,
                    "prediction_label": pred_label,
                    "probabilities": probabilities,
                    "latency_ms": latency_ms,
                })
        except Exception as db_err:
            logger.warning(f"Could not persist prediction log to database: {db_err}")

        return PredictionResponse(
            prediction=pred_class,
            prediction_label=pred_label,
            probabilities=probabilities,
            model_name=model_name,
            model_version=version,
            latency_ms=latency_ms,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc),
        )

    def predict_batch(
        self,
        request: BatchPredictionInput,
        correlation_id: Optional[str] = None
    ) -> BatchPredictionResponse:
        """Executes vector-accelerated batch inference."""
        correlation_id = correlation_id or str(uuid.uuid4())
        model_name = request.model_name or settings.DEFAULT_MODEL_NAME

        model_entry = self.registry.get_model(model_name, request.model_version)
        model = model_entry["model"]
        version = model_entry["metadata"].get("version", "1.0")

        X = batch_features_to_dataframe(request.items)

        start_time = time.perf_counter()
        pred_arr = model.predict(X)
        proba_arr = model.predict_proba(X)
        batch_latency_ms = round((time.perf_counter() - start_time) * 1000, 3)
        item_latency_ms = round(batch_latency_ms / len(request.items), 3)

        now = datetime.now(timezone.utc)
        results: List[PredictionResponse] = []
        for i in range(len(request.items)):
            pred_class = int(pred_arr[i])
            pred_label = TARGET_CLASSES[pred_class] if pred_class < len(TARGET_CLASSES) else str(pred_class)
            probs = {
                TARGET_CLASSES[j]: round(float(proba_arr[i][j]), 5)
                for j in range(len(proba_arr[i]))
            }
            results.append(
                PredictionResponse(
                    prediction=pred_class,
                    prediction_label=pred_label,
                    probabilities=probs,
                    model_name=model_name,
                    model_version=version,
                    latency_ms=item_latency_ms,
                    correlation_id=correlation_id,
                    timestamp=now,
                )
            )

        PREDICTION_COUNT.labels(model_name=model_name, model_version=version, status="batch_success").inc(len(request.items))
        return BatchPredictionResponse(
            predictions=results,
            total=len(results),
            model_name=model_name,
            model_version=version,
            batch_latency_ms=batch_latency_ms,
            correlation_id=correlation_id,
        )


prediction_service = PredictionService()
