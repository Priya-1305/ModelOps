# ModelOps Database Schema & Migrations

The platform utilizes **SQLAlchemy 2.x** declarative mapping and **Alembic** for schema migrations.

---

## 1. Entity-Relationship Diagram

```mermaid
erDiagram
    EXPERIMENTS ||--o{ TRAINING_RUNS : contains
    TRAINING_RUNS ||--o{ MODEL_VERSIONS : generates
    REGISTERED_MODELS ||--o{ MODEL_VERSIONS : has
    MODEL_VERSIONS ||--o{ DEPLOYMENTS : deployed_in
    MODEL_VERSIONS ||--o{ PREDICTION_LOGS : generates
    MODEL_VERSIONS ||--o{ MONITORING_REPORTS : evaluated_by

    EXPERIMENTS {
        string id PK "UUID"
        string name UK "Experiment Name"
        text description
        datetime created_at
    }

    TRAINING_RUNS {
        string id PK "UUID"
        string experiment_id FK
        string run_name
        string status
        string model_type
        json parameters
        json metrics
        json dataset_metadata
        string artifact_uri
        string mlflow_run_id
        datetime started_at
        datetime completed_at
        float duration_seconds
    }

    REGISTERED_MODELS {
        string id PK "UUID"
        string name UK "Model Name"
        text description
        datetime created_at
        datetime updated_at
    }

    MODEL_VERSIONS {
        string id PK "UUID"
        string registered_model_id FK
        string version_number
        string training_run_id FK
        string stage "candidate|staging|production|archived"
        json metrics
        json parameters
        string artifact_uri
        text description
        datetime created_at
        datetime promoted_at
    }

    DEPLOYMENTS {
        string id PK "UUID"
        string model_version_id FK
        string environment "production|staging"
        string status "active|rolled_back"
        datetime deployed_at
        string deployed_by
        json config
    }

    PREDICTION_LOGS {
        string id PK "UUID"
        string correlation_id "Indexed"
        string model_version_id FK
        string model_name
        string model_version
        json features
        int prediction
        string prediction_label
        json probabilities
        float latency_ms
        datetime timestamp "Indexed"
    }

    MONITORING_REPORTS {
        string id PK "UUID"
        string model_version_id FK
        string model_name
        string model_version
        string report_type
        bool data_drift_detected
        bool prediction_drift_detected
        float drift_share
        int drifted_features_count
        int total_features_count
        json metrics
        json summary
        string html_report_path
        datetime created_at "Indexed"
    }
```

---

## 2. Table Specifications & Indexes

### `experiments`
- `id` (VARCHAR(36), PK): UUID.
- `name` (VARCHAR(100), UNIQUE, INDEX): Human-readable experiment identifier.
- `created_at` (TIMESTAMPTZ): Ingestion timestamp.

### `training_runs`
- `id` (VARCHAR(36), PK): Unique run identifier.
- `experiment_id` (VARCHAR(36), FK -> `experiments.id`, ON DELETE CASCADE, INDEX).
- `parameters` (JSON): Hyperparameter key-value dictionary.
- `metrics` (JSON): Validation F1, ROC-AUC, accuracy, confusion matrix.
- `mlflow_run_id` (VARCHAR(100), INDEX): Link to external MLflow tracking instance.

### `registered_models`
- `id` (VARCHAR(36), PK): Unique model entity ID.
- `name` (VARCHAR(100), UNIQUE, INDEX): Canonical model namespace.

### `model_versions`
- `stage` (VARCHAR(50), INDEX): Lifecycle stage (`candidate`, `staging`, `production`, `archived`, `rejected`).
- Foreign key relationships to `registered_models` and `training_runs`.

### `prediction_logs`
- `correlation_id` (VARCHAR(100), INDEX): Enables end-to-end tracing across distributed microservices.
- `timestamp` (TIMESTAMPTZ, INDEX): Optimized for time-series range queries and drift calculation.

---

## 3. Migration Strategy with Alembic

1. **Creating Migrations**:
   ```bash
   alembic revision --autogenerate -m "Add new column"
   ```
2. **Applying Migrations**:
   ```bash
   alembic upgrade head
   ```
3. **Downgrading Migrations**:
   ```bash
   alembic downgrade -1
   ```
4. **Production Guidelines**:
   - Never edit an existing migration script that has already been deployed to staging or production.
   - Always run pre-deployment checks against an isolated staging replica.
