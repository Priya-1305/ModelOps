import pytest


def test_create_training_run_logistic_regression(client):
    payload = {
        "model_name": "breast_cancer_classifier",
        "model_type": "logistic_regression",
        "hyperparameters": {"C": 1.0, "max_iter": 200},
        "experiment_name": "breast_cancer_wisconsin",
        "tags": {"environment": "test", "author": "ci"},
        "auto_register": True,
    }
    response = client.post("/api/v1/training-runs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["model_type"] == "logistic_regression"
    assert "metrics" in data
    assert data["metrics"]["val_accuracy"] >= 0.85
    assert data["metrics"]["val_f1_score"] >= 0.85
    assert "dataset_metadata" in data
    assert data["dataset_metadata"]["total_samples"] == 569


def test_list_and_get_training_runs(client):
    # List runs
    list_res = client.get("/api/v1/training-runs")
    assert list_res.status_code == 200
    runs = list_res.json()
    assert isinstance(runs, list)
    assert len(runs) >= 1

    first_run_id = runs[0]["id"]

    # Get single run by ID
    get_res = client.get(f"/api/v1/training-runs/{first_run_id}")
    assert get_res.status_code == 200
    run_detail = get_res.json()
    assert run_detail["id"] == first_run_id
    assert "parameters" in run_detail
    assert "metrics" in run_detail


def test_list_experiments_returns_runs(client):
    exp_res = client.get("/api/v1/experiments")
    assert exp_res.status_code == 200
    exps = exp_res.json()
    assert isinstance(exps, list)
    assert len(exps) >= 1
    assert any(e["name"] == "breast_cancer_wisconsin" for e in exps)
