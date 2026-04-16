import pytest

from fastapi.testclient import TestClient
from app.main import app

from unittest.mock import patch
import numpy as np


class DummyModel:
    def predict(self, X):
        return np.array([1])

    def predict_proba(self, X):
        return np.array([[0.2, 0.8]])


@patch("app.core.lifecycle.load_model")
def test_health(mock_load_model):
    dummy_model = DummyModel()
    mock_load_model.return_value = (dummy_model, "models:/demo/1")
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"is_alive": True}

@patch("app.core.lifecycle.load_model")
def test_predict_success(mock_load_model):
    dummy_model = DummyModel()
    mock_load_model.return_value = (dummy_model, "models:/demo/1")
    
    with TestClient(app) as client:
        payload = {
            "feature1": 1.0,
            "feature2": 2.0,
            "request_id": "req-001"
        }
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 200

        data = resp.json()
        assert "prediction" in data
        assert "probability" in data
        assert "model_version" in data
        assert data["request_id"] == "req-001"
        assert isinstance(data["prediction"], int)
        assert isinstance(data["probability"], list)
        assert len(data["probability"]) > 0

@patch("app.core.lifecycle.load_model")
def test_predict_invalid_payload(mock_load_model):
    dummy_model = DummyModel()
    mock_load_model.return_value = (dummy_model, "models:/demo/1")
    with TestClient(app) as client:
        payload = {
            "feature1": "bad-value",
            "feature2": 2.0
        }
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

@patch("app.core.lifecycle.load_model")
def test_version(mock_load_model):
    dummy_model = DummyModel()
    mock_load_model.return_value = (dummy_model, "models:/demo/1")
    with TestClient(app) as client:
        resp = client.get("/version")
        assert resp.status_code == 200

        data = resp.json()
        assert "app_version" in data
        assert "model_version" in data
        assert "model_uri" in data
        assert "model_stage" in data
        assert "loaded_at" in data
        assert data["model_uri"] == "models:/demo/1"
        assert data["model_version"] == "1"
           
@patch("app.core.lifecycle.load_model")
def test_app_startup_fails_when_model_load_fails(mock_load_model):
    mock_load_model.side_effect = RuntimeError("Model file not found")

    with pytest.raises(RuntimeError, match="Model file not found"):
        with TestClient(app) as client:
            client.get("/health")
            
@patch("app.core.lifecycle.load_model")
def test_predict_missing_field(mock_load_model):
    dummy_model = DummyModel()
    mock_load_model.return_value = (dummy_model, "models:/demo/1")

    with TestClient(app) as client:
        payload = {
            "feature1": 1.0
        }
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422