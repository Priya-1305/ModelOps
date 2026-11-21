# ModelOps REST API Documentation

All endpoints are versioned under `/api/v1`. Interactive Swagger documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## Headers

| Header | Description | Default / Example |
|---|---|---|
| `X-Correlation-ID` | Unique request tracking identifier. If omitted, the server generates a new UUID. | `c4b12345-6789-4abc-def0-123456789abc` |
| `Content-Type` | MIME type for request payload. | `application/json` |

---

## 1. Health & Readiness

### Liveness Probe
`GET /api/v1/health`
- **Description**: Returns 200 OK if application process is responsive.
- **Response**:
```json
{
  "status": "HEALTHY",
  "service": "ModelOps Platform",
  "environment": "production",
  "timestamp": 1732085000.123
}
```

### Readiness Probe
`GET /api/v1/ready`
- **Description**: Verifies database connection and that an active production model is warmed into memory.
- **Response**:
```json
{
  "status": "READY",
  "ready": true,
  "uptime_seconds": 3600.5,
  "active_model": "breast_cancer_classifier",
  "active_version": "1.3885"
}
```

---

## 2. Model Inference

### Single Prediction
`POST /api/v1/predictions`
- **Request Body**:
```json
{
  "features": {
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
    "worst_fractal_dimension": 0.1189
  },
  "model_name": "breast_cancer_classifier",
  "model_version": "1.3885"
}
```
- **Response (200 OK)**:
```json
{
  "prediction": 0,
  "prediction_label": "malignant",
  "probabilities": {
    "malignant": 0.9452,
    "benign": 0.0548
  },
  "model_name": "breast_cancer_classifier",
  "model_version": "1.3885",
  "latency_ms": 2.14,
  "correlation_id": "c4b12345-6789-4abc-def0-123456789abc",
  "timestamp": "2026-11-20T12:00:00Z"
}
```

### Batch Predictions
`POST /api/v1/predictions/batch`
- **Request Body**:
```json
{
  "items": [
    { /* 30 features dictionary */ },
    { /* 30 features dictionary */ }
  ],
  "model_name": "breast_cancer_classifier"
}
```

---

## 3. Model Registry & Promotion

### List Registered Models
`GET /api/v1/models`

### Get Model Details
`GET /api/v1/models/{model_id}`

### Controlled Promotion Gate
`POST /api/v1/models/{model_id}/versions/{version}/promote`
- **Request Body**:
```json
{
  "target_stage": "production",
  "minimum_f1_score": 0.88,
  "minimum_roc_auc": 0.88,
  "force": false,
  "comment": "Passing Q4 benchmark acceptance criteria"
}
```
- **Response**: Returns 200 OK with updated version metadata, or 400 Bad Request if candidate fails quality gates.

### Rollback Model
`POST /api/v1/models/{model_id}/rollback`
- **Request Body**:
```json
{
  "target_version": "1.3880",
  "comment": "Reverting due to downstream telemetry check"
}
```

---

## 4. Training Pipeline & Experiments

### Trigger Training Run
`POST /api/v1/training-runs`
- **Request Body**:
```json
{
  "model_name": "breast_cancer_classifier",
  "model_type": "random_forest",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 5,
    "random_state": 42
  },
  "experiment_name": "breast_cancer_wisconsin",
  "auto_register": true
}
```

### List Training Runs
`GET /api/v1/training-runs?limit=50&offset=0`

### List Experiments
`GET /api/v1/experiments`

---

## 5. Monitoring & Drift Detection

### Statistical Drift Report
`GET /api/v1/monitoring/drift?threshold=0.3`
- **Description**: Runs two-sample Kolmogorov-Smirnov distribution tests comparing baseline training feature distributions against recent prediction logs.

### Trigger Controlled Retraining
`POST /api/v1/retraining/trigger`
- **Request Body**:
```json
{
  "reason": "Feature drift threshold exceeded on 8 columns",
  "model_name": "breast_cancer_classifier",
  "model_type": "random_forest"
}
```
- **Response**: Compares candidate metrics with active production metrics and issues recommendation (`RECOMMENDED_FOR_PROMOTION` or `REJECTED_BELOW_PRODUCTION`).
