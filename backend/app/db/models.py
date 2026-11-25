import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now()
    )

    runs: Mapped[List["TrainingRun"]] = relationship("TrainingRun", back_populates="experiment", cascade="all, delete-orphan")


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    run_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    dataset_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    artifact_uri: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mlflow_run_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="runs")
    model_versions: Mapped[List["ModelVersion"]] = relationship("ModelVersion", back_populates="training_run")


class RegisteredModel(Base):
    __tablename__ = "registered_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    versions: Mapped[List["ModelVersion"]] = relationship(
        "ModelVersion", back_populates="registered_model", cascade="all, delete-orphan", order_by="desc(ModelVersion.created_at)"
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    registered_model_id: Mapped[str] = mapped_column(ForeignKey("registered_models.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    training_run_id: Mapped[Optional[str]] = mapped_column(ForeignKey("training_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    stage: Mapped[str] = mapped_column(String(50), default="candidate", nullable=False, index=True)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    artifact_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now()
    )
    promoted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    registered_model: Mapped["RegisteredModel"] = relationship("RegisteredModel", back_populates="versions")
    training_run: Mapped[Optional["TrainingRun"]] = relationship("TrainingRun", back_populates="model_versions")
    deployments: Mapped[List["Deployment"]] = relationship("Deployment", back_populates="model_version")
    prediction_logs: Mapped[List["PredictionLog"]] = relationship("PredictionLog", back_populates="model_version_rel")
    monitoring_reports: Mapped[List["MonitoringReport"]] = relationship("MonitoringReport", back_populates="model_version_rel")


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    environment: Mapped[str] = mapped_column(String(50), default="production", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    deployed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now()
    )
    deployed_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    model_version: Mapped["ModelVersion"] = relationship("ModelVersion", back_populates="deployments")


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    model_version_id: Mapped[Optional[str]] = mapped_column(ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    features: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)
    prediction_label: Mapped[str] = mapped_column(String(50), nullable=False)
    probabilities: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), index=True
    )

    model_version_rel: Mapped[Optional["ModelVersion"]] = relationship("ModelVersion", back_populates="prediction_logs")


class MonitoringReport(Base):
    __tablename__ = "monitoring_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    model_version_id: Mapped[Optional[str]] = mapped_column(ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(50), default="data_drift", nullable=False)
    data_drift_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    prediction_drift_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    drift_share: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    drifted_features_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_features_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    html_report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), server_default=func.now(), index=True
    )

    model_version_rel: Mapped[Optional["ModelVersion"]] = relationship("ModelVersion", back_populates="monitoring_reports")
