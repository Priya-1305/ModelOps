from prometheus_client import Counter, Histogram, Gauge

# HTTP Request Metrics
REQUEST_COUNT = Counter(
    "modelops_http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "modelops_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# Model Serving & Prediction Metrics
PREDICTION_COUNT = Counter(
    "modelops_predictions_total",
    "Total predictions generated",
    ["model_name", "model_version", "status"],
)

PREDICTION_LATENCY = Histogram(
    "modelops_prediction_duration_seconds",
    "Model inference latency in seconds",
    ["model_name", "model_version"],
    buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
)

ACTIVE_MODEL_VERSION = Gauge(
    "modelops_active_model_version",
    "Active model deployment version indicator (1 for active)",
    ["model_name", "version"],
)

DRIFT_DETECTED = Gauge(
    "modelops_drift_detected",
    "Drift status indicator: 1 if drift detected, 0 otherwise",
    ["model_name", "version", "drift_type"],
)
