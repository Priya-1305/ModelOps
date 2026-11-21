# ModelOps Monitoring, Drift Detection & Observability

Observability in production machine learning encompasses both traditional backend performance metrics (latency, errors, throughput) and specialized ML data health indicators (covariate shift, prediction drift).

---

## 1. Distinguishing Types of Drift and Degradation

A fundamental mistake in ML engineering is treating feature drift as proof of model degradation. ModelOps makes explicit distinctions:

| Metric Type | Definition | Observable in Real-Time? | Implies Accuracy Loss? | Action Required |
|---|---|---|---|---|
| **Data Drift (Covariate Shift)** | Changes in the marginal distribution of inputs: $P(X_{current}) \neq P(X_{ref})$ | Yes (from input features alone) | **No.** If $P(Y \mid X)$ remains unchanged, the model may still perform accurately. | Investigate distribution shifts; assess if retraining is warranted. |
| **Prediction Drift** | Changes in the distribution of model outputs: $P(\hat{Y}_{current}) \neq P(\hat{Y}_{ref})$ | Yes (from model predictions) | **Maybe.** Could reflect natural population shift or genuine failure mode. | Analyze class distribution shifts and confidence spread. |
| **Performance Degradation** | Drop in actual ground truth metrics ($F_1$, Accuracy, $ROC\text{-}AUC$) | **No** (requires labeled outcomes) | **Yes.** Definitive proof of performance drop. | Immediate candidate evaluation, retraining, or rollback. |

---

## 2. Statistical Drift Testing Engine

ModelOps utilizes **Evidently** and **scipy.stats** for statistical drift testing:
- **Continuous Features**: Two-sample Kolmogorov-Smirnov (KS) test ($p\text{-value} < 0.05$ flags drift).
- **Dataset Drift Condition**: Dataset drift is triggered when more than $30\%$ of features (9+ of 30 features) exhibit statistically significant distribution shifts.
- **Evidently HTML Artifacts**: Complete visual HTML reports are saved to `artifacts/reports/` for deep exploratory analysis.

---

## 3. Prometheus Metrics Inventory

| Metric Name | Type | Labels | Description |
|---|---|---|---|
| `modelops_http_requests_total` | Counter | `method`, `endpoint`, `status_code` | Total HTTP requests received. |
| `modelops_http_request_duration_seconds` | Histogram | `endpoint` | End-to-end request latency. |
| `modelops_predictions_total` | Counter | `model_name`, `model_version`, `status` | Total predictions processed. |
| `modelops_prediction_duration_seconds` | Histogram | `model_name`, `model_version` | Model inference execution latency. |
| `modelops_active_model_version` | Gauge | `model_name`, `version` | Active production version indicator. |
| `modelops_drift_detected` | Gauge | `model_name`, `version`, `drift_type` | Drift alert status (1=alert, 0=normal). |

---

## 4. Grafana Dashboards

The Grafana instance is pre-provisioned via `docker-compose.yml` (`http://localhost:3001`):
1. **Total Predictions**: Real-time counter of requests served.
2. **Inference Latency Percentiles (p50, p95, p99)**: High-resolution latency histograms.
3. **HTTP Error Rate**: Percentage of $5xx$ status codes.
4. **Drift Alert Gauge**: Highlights when feature drift thresholds are breached.
5. **Version Traffic Distribution**: Stacked time-series breakdown of predictions by model version.
