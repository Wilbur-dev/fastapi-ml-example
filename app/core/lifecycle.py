from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.infrastructure.model.loader import load_model
from app.infrastructure.model.runtime import ModelRuntime
from app.services.inference_service import InferenceService

@asynccontextmanager
async def lifespan(app: FastAPI):
    model, model_path = load_model()
    runtime = ModelRuntime(model, model_path)
    service = InferenceService(runtime)

    app.state.inference_service = service

    yield