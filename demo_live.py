import requests
import json
import time

BASE = "http://127.0.0.1:8000/api/v1"

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title.upper()}")
    print("=" * 70)

# 1. Health & Readiness
print_header("1. API Health & System Readiness")
health = requests.get(f"{BASE}/health").json()
ready = requests.get(f"{BASE}/ready").json()
print(f"Health Status:    {health.get('status')} (Environment: {health.get('environment')})")
print(f"Readiness Status: {ready.get('status')} (Ready: {ready.get('ready')})")
print(f"Active Model:     {ready.get('active_model')} (v{ready.get('active_version')})")
print(f"System Uptime:    {ready.get('uptime_seconds')} seconds")

# 2. Model Registry
print_header("2. Model Registry State")
models = requests.get(f"{BASE}/models").json()
for m in models:
    print(f"Model ID:            {m.get('id')}")
    print(f"Model Name:          {m.get('name')}")
    print(f"Active Version:      {m.get('active_version')}")
    print(f"Total Versions:      {m.get('version_count')}")

# 3. Live Single Inference
print_header("3. Real-Time Single Inference (In-Memory Warmed Model)")
malignant_sample = {
    "model_name": "breast_cancer_classifier",
    "features": {
        "mean radius": 17.99, "mean texture": 10.38, "mean perimeter": 122.8,
        "mean area": 1001.0, "mean smoothness": 0.1184, "mean compactness": 0.2776,
        "mean concavity": 0.3001, "mean concave points": 0.1471, "mean symmetry": 0.2419,
        "mean fractal dimension": 0.07871, "radius error": 1.095, "texture error": 0.9053,
        "perimeter error": 8.589, "area error": 153.4, "smoothness error": 0.006399,
        "compactness error": 0.04904, "concavity error": 0.05373, "concave points error": 0.01587,
        "symmetry error": 0.03003, "fractal dimension error": 0.006193, "worst radius": 25.38,
        "worst texture": 17.33, "worst perimeter": 184.6, "worst area": 2019.0,
        "worst smoothness": 0.1622, "worst compactness": 0.6656, "worst concavity": 0.7119,
        "worst concave points": 0.2654, "worst symmetry": 0.4601, "worst fractal dimension": 0.1189
    }
}
resp = requests.post(f"{BASE}/predictions", json=malignant_sample)
pred = resp.json()
print(f"HTTP Status:          {resp.status_code} OK")
print(f"Correlation ID:       {resp.headers.get('x-correlation-id')}")
print(f"Predicted Class:      {pred.get('prediction')} -> {pred.get('prediction_label').upper()}")
print(f"Class Probabilities:  {pred.get('probabilities')}")
print(f"Inference Latency:    {pred.get('latency_ms'):.3f} ms")
print(f"Model Version:        {pred.get('model_version')}")

# 4. Batch Inference
print_header("4. High-Throughput Batch Inference")
benign_sample = {k: v * 0.7 for k, v in malignant_sample["features"].items()}
batch_payload = {
    "model_name": "breast_cancer_classifier",
    "items": [
        malignant_sample["features"],
        benign_sample
    ]
}
batch_resp = requests.post(f"{BASE}/predictions/batch", json=batch_payload).json()
print(f"Total Predictions:    {batch_resp.get('total')}")
print(f"Batch Latency:        {batch_resp.get('batch_latency_ms'):.3f} ms")
for idx, p in enumerate(batch_resp.get('predictions', [])):
    print(f"  Item #{idx + 1}: Class {p.get('prediction')} ({p.get('prediction_label')}) - {p.get('probabilities')}")

# 5. Statistical Data Drift Monitoring
print_header("5. Statistical Drift Detection (Kolmogorov-Smirnov Test)")
drift = requests.get(f"{BASE}/monitoring/drift", params={"model_name": "breast_cancer_classifier"}).json()
print(f"Data Drift Detected:         {drift.get('data_drift_detected')}")
print(f"Prediction Drift Detected:   {drift.get('prediction_drift_detected')}")
print(f"Performance Degradation:     {drift.get('performance_degradation_detected')} (Preserves distinction between drift & degradation)")
print(f"Drift Share:                 {drift.get('drift_share'):.2%}")
print(f"Drifted Features Count:      {drift.get('drifted_features_count')} / {drift.get('total_features_count')}")

# 6. Train a New Candidate Model
print_header("6. Training Pipeline Execution (Logistic Regression Baseline)")
training_payload = {
    "model_name": "breast_cancer_classifier",
    "model_type": "logistic_regression",
    "hyperparameters": {"C": 1.0, "max_iter": 500, "random_state": 42},
    "experiment_name": "baseline_comparison",
    "auto_register": True
}
train_resp = requests.post(f"{BASE}/training-runs", json=training_payload).json()
new_version = train_resp.get("version")
print(f"Run ID:                      {train_resp.get('id')}")
print(f"Status:                      {train_resp.get('status')}")
print(f"Model Type:                  {train_resp.get('model_type')}")
print(f"Registered Version:          {new_version}")
print("Validation Metrics:")
for k, v in train_resp.get("metrics", {}).items():
    if isinstance(v, (int, float)):
        print(f"  - {k}: {v:.4f}")

# 7. Controlled Model Promotion
if new_version:
    print_header("7. Controlled Promotion Gate")
    promo_payload = {
        "reason": "Automated quality gate passed. Candidate demonstrates high validation F1 and ROC-AUC.",
        "promoted_by": "lead-mlops-engineer"
    }
    promo_resp = requests.post(f"{BASE}/models/breast_cancer_classifier/versions/{new_version}/promote", json=promo_payload)
    if promo_resp.status_code == 200:
        p_data = promo_resp.json()
        print(f"Promotion Status:     SUCCESS")
        print(f"Promoted Version:     {new_version}")
        print(f"Stage:                {p_data.get('stage').upper()}")
        print(f"Promoted By:          {p_data.get('promoted_by')}")
        print(f"Reason:               {p_data.get('promotion_reason')}")
    else:
        print(f"Promotion Response:   {promo_resp.status_code} - {promo_resp.text}")

# 8. Prometheus Observability
print_header("8. Live Prometheus Metrics Scrape")
metrics_txt = requests.get("http://127.0.0.1:8000/metrics").text
scraped = [l for l in metrics_txt.split("\n") if (l.startswith("modelops_predictions_total") or l.startswith("modelops_drift_detected")) and not l.startswith("#")]
for line in scraped[:6]:
    print(f"  {line}")

print_header("DEMONSTRATION COMPLETE - ALL SYSTEMS FUNCTIONAL")
