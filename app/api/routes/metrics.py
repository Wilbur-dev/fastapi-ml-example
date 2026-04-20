from fastapi import APIRouter
from app.observability.metrics import metrics_response

router = APIRouter()

@router.get("/metrics", name="metrics")
def metrics():
    return metrics_response()