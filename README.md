# fastapi-ml-example

A production-style example project for serving a machine learning model with **FastAPI**.

This project demonstrates how to package a simple ML inference workflow into a clean backend service, including API design, model loading, request validation, health checks, and local development setup.

---

## Features

- FastAPI-based REST API for model inference
- Clear project structure for backend + ML serving
- Request/response schema validation with Pydantic
- Health check endpoint for service monitoring
- Ready for local development and future Docker deployment
- Simple example for learning ML model serving fundamentals

---

## Tech Stack

- **Python**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **Scikit-learn** / ML model artifact
- **Git**

---

## Project Structure

```bash
fastapi-ml-example/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── infrastructure/
│   │   └── model/
│   ├── models/
│   ├── services/
│   └── main.py
├── training/
│   └── train_ml_model.py
├── models/
│   └── lr_model.joblib
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```


## Run with Docker
```bash
docker compose up --build
```


## Run Tests
```bash
docker compose up --build -d
docker compose run --rm api pytest -q
```

## Example Requests:
- curl http://localhost:8000/health
- curl http://localhost:8000/version
- curl -X POST http://localhost:8000/predict \
-H "Content-Type: application/json" \
-d '{"feature1": 1.0, "feature2": 2.0, "request_id": "req-001"}'