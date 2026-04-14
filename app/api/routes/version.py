from fastapi import APIRouter, Request
from app.models.version import VersionResult

router = APIRouter()

@router.get("/version", response_model=VersionResult, name="version")
def version(request: Request) -> VersionResult:
    service = request.app.state.inference_service
    runtime = service.runtime

    return VersionResult(
        
        app_version=runtime.app_version,
        model_version=runtime.model_version,
        model_uri=runtime.model_uri,
        model_stage=runtime.model_stage,
        loaded_at=runtime.loaded_at,
    )