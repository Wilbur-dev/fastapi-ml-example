from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"is_alive": True}

def test_predict_success():
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

def test_predict_invalid_payload():
    with TestClient(app) as client:
        payload = {
            "feature1": "bad-value",
            "feature2": 2.0
        }
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

def test_version():
    with TestClient(app) as client:
        resp = client.get("/version")
        assert resp.status_code == 200

        data = resp.json()
        assert "app_version" in data
        assert "model_version" in data
        assert "model_path" in data