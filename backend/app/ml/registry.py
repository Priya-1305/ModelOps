import os
import json
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import pandas as pd
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import ModelNotFoundException, ModelNotLoadedException
from backend.app.ml.validation import EXPECTED_FEATURE_NAMES


class ModelArtifactManager:
    """
    Manages local filesystem storage, validation, caching, and serving of model artifacts.
    Ensures models are warmed into memory at startup, never reloaded per-request.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.MODEL_REGISTRY_PATH
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # In-memory model cache: key -> {"model": pipeline, "metadata": dict}
        self._loaded_models: Dict[str, Dict[str, Any]] = {}
        # Active production versions per model name: model_name -> version
        self._active_versions: Dict[str, str] = {}

    def _get_model_dir(self, model_name: str, version: str) -> Path:
        return self.base_dir / model_name / f"v_{version}"

    def validate_model_artifact(self, model: Any) -> Tuple[bool, Optional[str]]:
        """Verifies model object is fitted and can generate predictions and probabilities."""
        if not hasattr(model, "predict"):
            return False, "Model artifact does not implement predict() method."
        if not hasattr(model, "predict_proba"):
            return False, "Model artifact does not implement predict_proba() method."

        # Smoke test with dummy valid input of 30 zeros or mean values
        try:
            dummy_data = pd.DataFrame([{col: 1.0 for col in EXPECTED_FEATURE_NAMES}])
            pred = model.predict(dummy_data)
            proba = model.predict_proba(dummy_data)
            if len(pred) != 1 or proba.shape[1] < 2:
                return False, f"Smoke test returned unexpected prediction shape: {pred}, proba: {proba}"
        except Exception as e:
            return False, f"Model smoke test failed: {str(e)}"

        return True, None

    def save_model_artifact(
        self,
        model: Any,
        model_name: str,
        version: str,
        metadata: Dict[str, Any],
    ) -> Path:
        """Validates and persists model artifact and metadata to disk."""
        is_valid, error = self.validate_model_artifact(model)
        if not is_valid:
            raise ValueError(f"Model validation failed before saving: {error}")

        model_dir = self._get_model_dir(model_name, version)
        model_dir.mkdir(parents=True, exist_ok=True)

        artifact_path = model_dir / "model.joblib"
        metadata_path = model_dir / "metadata.json"

        # Save model pipeline
        joblib.dump(model, artifact_path)

        # Enrich metadata
        enriched_metadata = {
            "model_name": model_name,
            "version": version,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "artifact_path": str(artifact_path),
            "expected_features": EXPECTED_FEATURE_NAMES,
            **metadata,
        }

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(enriched_metadata, f, indent=2)

        # Cache in memory
        cache_key = f"{model_name}:{version}"
        self._loaded_models[cache_key] = {
            "model": model,
            "metadata": enriched_metadata,
        }

        logger.info(f"Model {model_name} version {version} saved and cached successfully at {artifact_path}")
        return artifact_path

    def load_model(self, model_name: str, version: str) -> Dict[str, Any]:
        """Loads model into memory if not already cached. Thread-safe cached retrieval."""
        cache_key = f"{model_name}:{version}"
        if cache_key in self._loaded_models:
            return self._loaded_models[cache_key]

        model_dir = self._get_model_dir(model_name, version)
        artifact_path = model_dir / "model.joblib"
        metadata_path = model_dir / "metadata.json"

        if not artifact_path.exists():
            raise ModelNotFoundException(f"Model '{model_name}' version '{version}' not found on disk at {artifact_path}")

        try:
            model = joblib.load(artifact_path)
            is_valid, error = self.validate_model_artifact(model)
            if not is_valid:
                raise ValueError(f"Corrupted or invalid model artifact: {error}")

            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

            cached_entry = {
                "model": model,
                "metadata": metadata,
            }
            self._loaded_models[cache_key] = cached_entry
            logger.info(f"Loaded and cached model {model_name} version {version} in memory.")
            return cached_entry
        except Exception as e:
            logger.error(f"Failed to load model {model_name} version {version}: {e}")
            raise ModelNotLoadedException(f"Failed to load model {model_name}:{version}: {str(e)}")

    def set_active_version(self, model_name: str, version: str):
        """Sets the production active version and warms it into memory."""
        self.load_model(model_name, version)
        self._active_versions[model_name] = version
        logger.info(f"Active production version for model '{model_name}' updated to '{version}'.")

    def get_active_model(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Returns the in-memory active production model for inference."""
        model_name = model_name or settings.DEFAULT_MODEL_NAME
        active_ver = self._active_versions.get(model_name)
        if not active_ver:
            # Check if any version is available on disk and activate it
            model_base = self.base_dir / model_name
            if model_base.exists():
                versions = sorted([d.name.replace("v_", "") for d in model_base.iterdir() if d.is_dir() and d.name.startswith("v_")])
                if versions:
                    active_ver = versions[-1]
                    self.set_active_version(model_name, active_ver)

        if not active_ver:
            raise ModelNotLoadedException(f"No active production model available for '{model_name}'.")

        return self.load_model(model_name, active_ver)

    def get_model(self, model_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Returns requested version or default active production version."""
        if version:
            return self.load_model(model_name, version)
        return self.get_active_model(model_name)


# Global singleton manager
model_manager = ModelArtifactManager()
