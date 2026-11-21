import pytest


def test_predict_single_success(client, valid_features_dict):
    payload = {
        "features": valid_features_dict
    }
    response = client.post("/api/v1/predictions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["prediction"] in [0, 1]
    assert data["prediction_label"] in ["malignant", "benign"]
    assert "probabilities" in data
    assert "malignant" in data["probabilities"]
    assert "benign" in data["probabilities"]
    assert "latency_ms" in data
    assert data["latency_ms"] > 0
    assert "correlation_id" in data
    # Header should also contain correlation ID
    assert response.headers.get("X-Correlation-ID") == data["correlation_id"]


def test_predict_custom_correlation_id_propagates(client, valid_features_dict):
    custom_cid = "client-test-corr-id-12345"
    payload = {"features": valid_features_dict}
    response = client.post(
        "/api/v1/predictions",
        json=payload,
        headers={"X-Correlation-ID": custom_cid}
    )
    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == custom_cid
    assert response.json()["correlation_id"] == custom_cid


def test_predict_fails_with_invalid_features(client):
    payload = {
        "features": {
            "mean_radius": -10.0,
            "mean_texture": 10.0,
        }
    }
    response = client.post("/api/v1/predictions", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data


def test_batch_prediction_success(client, valid_features_dict):
    batch_payload = {
        "items": [valid_features_dict, valid_features_dict, valid_features_dict]
    }
    response = client.post("/api/v1/predictions/batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["predictions"]) == 3
    assert data["batch_latency_ms"] > 0
