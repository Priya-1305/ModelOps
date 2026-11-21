from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from backend.app.db.models import (
    Experiment,
    TrainingRun,
    RegisteredModel,
    ModelVersion,
    Deployment,
    PredictionLog,
    MonitoringReport,
)


class ModelOpsRepository:
    def __init__(self, db: Session):
        self.db = db

    # Experiments
    def get_or_create_experiment(self, name: str, description: Optional[str] = None) -> Experiment:
        stmt = select(Experiment).where(Experiment.name == name)
        exp = self.db.scalars(stmt).first()
        if not exp:
            exp = Experiment(name=name, description=description)
            self.db.add(exp)
            self.db.commit()
            self.db.refresh(exp)
        return exp

    def list_experiments(self) -> List[Experiment]:
        stmt = select(Experiment).order_by(desc(Experiment.created_at))
        return list(self.db.scalars(stmt).all())

    # Training Runs
    def create_training_run(self, run_data: Dict[str, Any]) -> TrainingRun:
        run = TrainingRun(**run_data)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_training_run(self, run_id: str) -> Optional[TrainingRun]:
        stmt = select(TrainingRun).where(TrainingRun.id == run_id)
        return self.db.scalars(stmt).first()

    def list_training_runs(self, experiment_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[TrainingRun]:
        stmt = select(TrainingRun)
        if experiment_id:
            stmt = stmt.where(TrainingRun.experiment_id == experiment_id)
        stmt = stmt.order_by(desc(TrainingRun.started_at)).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    # Registered Models
    def get_or_create_registered_model(self, name: str, description: Optional[str] = None) -> RegisteredModel:
        stmt = select(RegisteredModel).where(RegisteredModel.name == name)
        model = self.db.scalars(stmt).first()
        if not model:
            model = RegisteredModel(name=name, description=description)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
        return model

    def list_registered_models(self) -> List[RegisteredModel]:
        stmt = select(RegisteredModel).order_by(desc(RegisteredModel.updated_at))
        return list(self.db.scalars(stmt).all())

    def get_registered_model_by_id_or_name(self, model_id_or_name: str) -> Optional[RegisteredModel]:
        stmt = select(RegisteredModel).where(
            (RegisteredModel.id == model_id_or_name) | (RegisteredModel.name == model_id_or_name)
        )
        return self.db.scalars(stmt).first()

    # Model Versions
    def create_model_version(self, version_data: Dict[str, Any]) -> ModelVersion:
        version = ModelVersion(**version_data)
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def get_model_version(self, model_id: str, version_number: str) -> Optional[ModelVersion]:
        stmt = select(ModelVersion).join(RegisteredModel).where(
            ((RegisteredModel.id == model_id) | (RegisteredModel.name == model_id))
            & (ModelVersion.version_number == version_number)
        )
        return self.db.scalars(stmt).first()

    def get_model_version_by_id(self, version_id: str) -> Optional[ModelVersion]:
        stmt = select(ModelVersion).where(ModelVersion.id == version_id)
        return self.db.scalars(stmt).first()

    def list_model_versions(self, model_id_or_name: str) -> List[ModelVersion]:
        stmt = select(ModelVersion).join(RegisteredModel).where(
            (RegisteredModel.id == model_id_or_name) | (RegisteredModel.name == model_id_or_name)
        ).order_by(desc(ModelVersion.created_at))
        return list(self.db.scalars(stmt).all())

    def get_active_production_version(self, model_name: str) -> Optional[ModelVersion]:
        stmt = select(ModelVersion).join(RegisteredModel).where(
            (RegisteredModel.name == model_name) & (ModelVersion.stage == "production")
        ).order_by(desc(ModelVersion.promoted_at))
        return self.db.scalars(stmt).first()

    # Deployments
    def create_deployment(self, deployment_data: Dict[str, Any]) -> Deployment:
        deployment = Deployment(**deployment_data)
        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)
        return deployment

    def list_deployments(self, limit: int = 50) -> List[Deployment]:
        stmt = select(Deployment).order_by(desc(Deployment.deployed_at)).limit(limit)
        return list(self.db.scalars(stmt).all())

    # Prediction Logs
    def create_prediction_log(self, log_data: Dict[str, Any]) -> PredictionLog:
        log = PredictionLog(**log_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_prediction_logs(
        self,
        model_version: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PredictionLog]:
        stmt = select(PredictionLog)
        if model_version:
            stmt = stmt.where(PredictionLog.model_version == model_version)
        stmt = stmt.order_by(desc(PredictionLog.timestamp)).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def count_prediction_logs(self, model_version: Optional[str] = None) -> int:
        from sqlalchemy import func
        stmt = select(func.count(PredictionLog.id))
        if model_version:
            stmt = stmt.where(PredictionLog.model_version == model_version)
        return self.db.scalar(stmt) or 0

    # Monitoring Reports
    def create_monitoring_report(self, report_data: Dict[str, Any]) -> MonitoringReport:
        report = MonitoringReport(**report_data)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def list_monitoring_reports(self, limit: int = 50) -> List[MonitoringReport]:
        stmt = select(MonitoringReport).order_by(desc(MonitoringReport.created_at)).limit(limit)
        return list(self.db.scalars(stmt).all())
