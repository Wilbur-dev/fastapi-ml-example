from fastapi import APIRouter
from app.api.routes import index, heartbeat, prediction, version, metrics


api = APIRouter()
api.include_router(index.router, tags=["index"])
api.include_router(heartbeat.router, tags=["health"])
api.include_router(prediction.router, tags=["prediction"])
api.include_router(version.router, tags=["version"])
api.include_router(metrics.router, tags=["metrics"])