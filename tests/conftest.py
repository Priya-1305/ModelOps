import pytest
import os
import sys
from pathlib import Path
from typing import Dict, Any
from fastapi.testclient import TestClient

# Ensure root is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Set test environment
TEST_DB_PATH = ROOT_DIR / "artifacts" / "test_modelops.db"
if TEST_DB_PATH.exists():
    try:
        TEST_DB_PATH.unlink()
    except Exception:
        pass

os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
os.environ["MLFLOW_TRACKING_URI"] = f"sqlite:///{(ROOT_DIR / 'artifacts' / 'test_mlflow.db').as_posix()}"

from backend.app.db.session import init_db
init_db()

from backend.app.main import app
from backend.app.ml.validation import EXPECTED_FEATURE_NAMES


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient with lifespan context."""
    with TestClient(app) as test_client:
        from backend.app.schemas.training import TrainingRunCreate
        from backend.app.services.training_service import training_service
        from backend.app.services.model_service import model_service
        from backend.app.schemas.model import PromotionRequest
        from backend.app.db.session import SessionLocal
        from backend.app.db.repository import ModelOpsRepository
        with SessionLocal() as db:
            repo = ModelOpsRepository(db)
            if not repo.list_registered_models():
                run = training_service.train_model(TrainingRunCreate(
                    model_name="breast_cancer_classifier",
                    model_type="random_forest",
                    hyperparameters={"n_estimators": 20, "max_depth": 3, "random_state": 42},
                    auto_register=True
                ))
                if run.get("version"):
                    model_service.promote_model_version(
                        "breast_cancer_classifier",
                        run["version"],
                        PromotionRequest(target_stage="production", minimum_f1_score=0.8, minimum_roc_auc=0.8),
                        db
                    )
        yield test_client


@pytest.fixture
def valid_features_dict() -> Dict[str, float]:
    """Provides a valid feature dictionary for Wisconsin Breast Cancer dataset."""
    sample = {
        "mean_radius": 17.99,
        "mean_texture": 10.38,
        "mean_perimeter": 122.8,
        "mean_area": 1001.0,
        "mean_smoothness": 0.1184,
        "mean_compactness": 0.2776,
        "mean_concavity": 0.3001,
        "mean_concave_points": 0.1471,
        "mean_symmetry": 0.2419,
        "mean_fractal_dimension": 0.07871,
        "radius_error": 1.095,
        "texture_error": 0.9053,
        "perimeter_error": 8.589,
        "area_error": 153.4,
        "smoothness_error": 0.006399,
        "compactness_error": 0.04904,
        "concavity_error": 0.05373,
        "concave_points_error": 0.01587,
        "symmetry_error": 0.03003,
        "fractal_dimension_error": 0.006193,
        "worst_radius": 25.38,
        "worst_texture": 17.33,
        "worst_perimeter": 184.6,
        "worst_area": 2019.0,
        "worst_smoothness": 0.1622,
        "worst_compactness": 0.6656,
        "worst_concavity": 0.7119,
        "worst_concave_points": 0.2654,
        "worst_symmetry": 0.4601,
        "worst_fractal_dimension": 0.1189,
    }
    return sample


@pytest.fixture
def benign_sample_features() -> Dict[str, float]:
    """Typical benign tumor feature values."""
    return {col: 0.5 for col in EXPECTED_FEATURE_NAMES}
