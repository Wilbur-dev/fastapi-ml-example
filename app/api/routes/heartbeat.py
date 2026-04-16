from fastapi import APIRouter
from app.api.schemas.healthcheck import HealthResult

router = APIRouter()

@router.get("/health", response_model=HealthResult, name='health')
def heartbeat() -> HealthResult:
    return HealthResult(is_alive=True)
