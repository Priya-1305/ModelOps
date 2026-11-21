import os
from pathlib import Path
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    API_V1_PREFIX: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="ModelOps Platform")
    API_KEY: str = Field(default="modelops-dev-secret-key")

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "*"]
    )

    DATABASE_URL: str = Field(default="sqlite:///./modelops.db")
    DB_ECHO: bool = Field(default=False)

    MLFLOW_TRACKING_URI: str = Field(default=f"sqlite:///{(BASE_DIR / 'artifacts' / 'mlflow.db').as_posix()}")
    MLFLOW_EXPERIMENT_NAME: str = Field(default="breast_cancer_wisconsin")

    ARTIFACT_STORE_PATH: Path = Field(default=BASE_DIR / "artifacts")
    MODEL_REGISTRY_PATH: Path = Field(default=BASE_DIR / "artifacts" / "models")
    EVIDENTLY_REPORTS_PATH: Path = Field(default=BASE_DIR / "artifacts" / "reports")

    DEFAULT_MODEL_NAME: str = Field(default="breast_cancer_classifier")
    DEFAULT_MODEL_TYPE: str = Field(default="random_forest")

    PROMETHEUS_METRICS_PATH: str = Field(default="/metrics")

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure directories exist
settings.ARTIFACT_STORE_PATH.mkdir(parents=True, exist_ok=True)
settings.MODEL_REGISTRY_PATH.mkdir(parents=True, exist_ok=True)
settings.EVIDENTLY_REPORTS_PATH.mkdir(parents=True, exist_ok=True)
