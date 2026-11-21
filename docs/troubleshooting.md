# ModelOps Troubleshooting & Runbook

Common failure modes, diagnostic steps, and resolutions for platform engineers.

---

## 1. Model Loading & Inference Issues

### Symptom: `503 Service Unavailable - Model is not loaded`
- **Cause**: No active model artifact has been registered or loaded into memory.
- **Diagnostic**:
  ```bash
  curl -s http://localhost:8000/api/v1/ready
  ```
- **Resolution**:
  Trigger a training run to generate and warm an initial production candidate:
  ```bash
  curl -X POST http://localhost:8000/api/v1/training-runs \
    -H "Content-Type: application/json" \
    -d '{"model_name":"breast_cancer_classifier","model_type":"random_forest","auto_register":true}'
  ```

### Symptom: `422 Unprocessable Entity - Validation failed`
- **Cause**: Missing features or invalid numerical values (NaN, Inf, or negative radius).
- **Diagnostic**: Inspect response payload `error.details` for the list of missing or out-of-bound column names.
- **Resolution**: Verify that all 30 expected Wisconsin Breast Cancer features are present and numeric.

---

## 2. Database & Migration Issues

### Symptom: `no such table: registered_models`
- **Cause**: Alembic migrations have not been applied to the current database.
- **Resolution**:
  ```bash
  alembic upgrade head
  ```

### Symptom: PostgreSQL connection refused in Docker
- **Cause**: The backend container attempted to connect before the PostgreSQL healthcheck completed.
- **Resolution**: In `docker-compose.yml`, verify that `backend` specifies:
  ```yaml
  depends_on:
    postgres:
      condition: service_healthy
  ```

---

## 3. MLflow Tracking Failures

### Symptom: `MlflowException: The filesystem tracking backend is in maintenance mode`
- **Cause**: MLflow 2.14+ deprecated raw filesystem `./mlruns` stores without a database backend.
- **Resolution**:
  Configure MLflow tracking URI to use SQLite (`sqlite:///artifacts/mlflow.db`) or PostgreSQL (`postgresql://...`). ModelOps sets `MLFLOW_ALLOW_FILE_STORE=true` and `MLFLOW_DISABLE_AGENT_HINT=1` as environment guardrails.

---

## 4. Evidently Statistical Drift Testing

### Symptom: Statistical test warnings during drift execution
- **Cause**: Evidently automated preset encountered minor numpy/pandas version deprecations.
- **Resolution**: The ModelOps `MonitoringService` implements an automatic, resilient fallback to scipy's two-sample Kolmogorov-Smirnov (`stats.ks_2samp`) engine, ensuring that statistical drift calculations never crash the service.
