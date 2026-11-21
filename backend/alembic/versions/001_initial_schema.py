"""Initial ModelOps Database Schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Experiments
    op.create_table(
        'experiments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiments_name'), 'experiments', ['name'], unique=True)

    # 2. Training Runs
    op.create_table(
        'training_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('experiment_id', sa.String(length=36), nullable=False),
        sa.Column('run_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('dataset_metadata', sa.JSON(), nullable=False),
        sa.Column('artifact_uri', sa.String(length=500), nullable=True),
        sa.Column('mlflow_run_id', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['experiment_id'], ['experiments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_runs_experiment_id'), 'training_runs', ['experiment_id'], unique=False)
    op.create_index(op.f('ix_training_runs_mlflow_run_id'), 'training_runs', ['mlflow_run_id'], unique=False)

    # 3. Registered Models
    op.create_table(
        'registered_models',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_registered_models_name'), 'registered_models', ['name'], unique=True)

    # 4. Model Versions
    op.create_table(
        'model_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('registered_model_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.String(length=50), nullable=False),
        sa.Column('training_run_id', sa.String(length=36), nullable=True),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('artifact_uri', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('promoted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['registered_model_id'], ['registered_models.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['training_run_id'], ['training_runs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_model_versions_registered_model_id'), 'model_versions', ['registered_model_id'], unique=False)
    op.create_index(op.f('ix_model_versions_stage'), 'model_versions', ['stage'], unique=False)
    op.create_index(op.f('ix_model_versions_training_run_id'), 'model_versions', ['training_run_id'], unique=False)
    op.create_index(op.f('ix_model_versions_version_number'), 'model_versions', ['version_number'], unique=False)

    # 5. Deployments
    op.create_table(
        'deployments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('model_version_id', sa.String(length=36), nullable=False),
        sa.Column('environment', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('deployed_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('deployed_by', sa.String(length=100), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deployments_model_version_id'), 'deployments', ['model_version_id'], unique=False)

    # 6. Prediction Logs
    op.create_table(
        'prediction_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('correlation_id', sa.String(length=100), nullable=False),
        sa.Column('model_version_id', sa.String(length=36), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('features', sa.JSON(), nullable=False),
        sa.Column('prediction', sa.Integer(), nullable=False),
        sa.Column('prediction_label', sa.String(length=50), nullable=False),
        sa.Column('probabilities', sa.JSON(), nullable=False),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prediction_logs_correlation_id'), 'prediction_logs', ['correlation_id'], unique=False)
    op.create_index(op.f('ix_prediction_logs_model_name'), 'prediction_logs', ['model_name'], unique=False)
    op.create_index(op.f('ix_prediction_logs_model_version'), 'prediction_logs', ['model_version'], unique=False)
    op.create_index(op.f('ix_prediction_logs_model_version_id'), 'prediction_logs', ['model_version_id'], unique=False)
    op.create_index(op.f('ix_prediction_logs_timestamp'), 'prediction_logs', ['timestamp'], unique=False)

    # 7. Monitoring Reports
    op.create_table(
        'monitoring_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('model_version_id', sa.String(length=36), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('data_drift_detected', sa.Boolean(), nullable=False),
        sa.Column('prediction_drift_detected', sa.Boolean(), nullable=False),
        sa.Column('drift_share', sa.Float(), nullable=False),
        sa.Column('drifted_features_count', sa.Integer(), nullable=False),
        sa.Column('total_features_count', sa.Integer(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('summary', sa.JSON(), nullable=False),
        sa.Column('html_report_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['model_version_id'], ['model_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monitoring_reports_created_at'), 'monitoring_reports', ['created_at'], unique=False)
    op.create_index(op.f('ix_monitoring_reports_model_name'), 'monitoring_reports', ['model_name'], unique=False)
    op.create_index(op.f('ix_monitoring_reports_model_version'), 'monitoring_reports', ['model_version'], unique=False)
    op.create_index(op.f('ix_monitoring_reports_model_version_id'), 'monitoring_reports', ['model_version_id'], unique=False)


def downgrade() -> None:
    op.drop_table('monitoring_reports')
    op.drop_table('prediction_logs')
    op.drop_table('deployments')
    op.drop_table('model_versions')
    op.drop_table('registered_models')
    op.drop_table('training_runs')
    op.drop_table('experiments')
