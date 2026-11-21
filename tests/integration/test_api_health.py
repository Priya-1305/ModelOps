import pytest


def test_health_check_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "environment" in data


def test_ready_check_returns_200_and_warmed_model(client):
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert data["ready"] is True
    assert data["active_model"] == "breast_cancer_classifier"
    assert data["active_version"] is not None


def test_prometheus_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "modelops_http_requests_total" in response.text
    assert "modelops_active_model_version" in response.text
