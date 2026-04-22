from unittest.mock import patch
import numpy as np
from fastapi.testclient import TestClient


class DummyModel:
    def predict(self, X):
        return np.array([1])

    def predict_proba(self, X):
        return np.array([[0.2, 0.8]])


@patch("app.core.lifecycle.load_model")
def test_app_startup_smoke(mock_load_model):
    mock_load_model.return_value = (DummyModel(), "models:/demo/1")

    from app.main import app

    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/version").status_code == 200