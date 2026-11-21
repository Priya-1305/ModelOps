import pytest


def test_list_models_returns_registered_model(client):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "breast_cancer_classifier"


def test_get_model_details(client):
    response = client.get("/api/v1/models/breast_cancer_classifier")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "breast_cancer_classifier"
    assert "versions" in data
    assert len(data["versions"]) >= 1


def test_model_promotion_and_rollback_flow(client):
    # 1. Trigger training run to produce a fresh candidate
    train_res = client.post(
        "/api/v1/training-runs",
        json={
            "model_name": "breast_cancer_classifier",
            "model_type": "random_forest",
            "hyperparameters": {"n_estimators": 20, "max_depth": 3, "random_state": 42},
            "auto_register": True,
        }
    )
    assert train_res.status_code == 201
    candidate_version = train_res.json()["version"]
    assert candidate_version is not None

    # 2. Try promotion with unrealistically high gate -> Should be rejected
    reject_res = client.post(
        f"/api/v1/models/breast_cancer_classifier/versions/{candidate_version}/promote",
        json={
            "target_stage": "production",
            "minimum_f1_score": 0.9999,
            "minimum_roc_auc": 0.9999,
            "force": False,
        }
    )
    assert reject_res.status_code == 400
    assert "Candidate model rejected by automated quality gate" in reject_res.json()["error"]["message"]

    # 3. Promote candidate with realistic passing gate
    promote_res = client.post(
        f"/api/v1/models/breast_cancer_classifier/versions/{candidate_version}/promote",
        json={
            "target_stage": "production",
            "minimum_f1_score": 0.85,
            "minimum_roc_auc": 0.85,
            "force": False,
            "comment": "Passing standard production quality gate."
        }
    )
    assert promote_res.status_code == 200
    promoted_data = promote_res.json()
    assert promoted_data["stage"] == "production"
    assert promoted_data["version"] == candidate_version

    # Verify model details shows this version as active
    details_res = client.get("/api/v1/models/breast_cancer_classifier")
    assert details_res.status_code == 200
    assert details_res.json()["active_version"] == candidate_version

    # 4. Rollback to previous version
    rollback_res = client.post(
        "/api/v1/models/breast_cancer_classifier/rollback",
        json={"comment": "Rollback test"}
    )
    assert rollback_res.status_code == 200
    assert rollback_res.json()["stage"] == "production"
