import pytest


def test_openapi_schema_contract(client):
    """Verifies OpenAPI contract conforms to standard REST specifications."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/ready" in schema["paths"]
    assert "/api/v1/predictions" in schema["paths"]
    assert "/api/v1/models" in schema["paths"]
    assert "/api/v1/models/{model_id}" in schema["paths"]
    assert "/api/v1/training-runs" in schema["paths"]
    assert "/api/v1/experiments" in schema["paths"]
    assert "/api/v1/monitoring/drift" in schema["paths"]


def test_prediction_contract_error_response_format(client):
    """Verifies that API error responses strictly conform to uniform error schema."""
    response = client.post("/api/v1/predictions", json={"features": {}})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "type" in data["error"]
    assert "message" in data["error"]
    assert "correlation_id" in data["error"]
