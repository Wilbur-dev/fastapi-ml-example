from fastapi import APIRouter, Request
from app.models.version import VersionResult

router = APIRouter()

@router.get("/version", response_model=VersionResult, name="version")
def version(request: Request) -> VersionResult:
    service = request.app.state.inference_service
    runtime = service.runtime

    return VersionResult(
        app_version="v1",
        model_version=runtime.model_version,
        model_path=runtime.model_path,
    )