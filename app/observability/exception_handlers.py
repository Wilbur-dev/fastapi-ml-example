from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.observability.metrics import ERROR_COUNT, REQUEST_COUNT


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        service = getattr(request.app.state, "inference_service", None)
        runtime = getattr(service, "runtime", None)

        model_version = getattr(runtime, "model_version", "unknown")
        release_track = getattr(runtime, "release_track", "unknown")

        ERROR_COUNT.labels(
            endpoint=request.url.path,
            method=request.method,
            status_bucket="4xx",
            model_version=model_version,
            release_track=release_track,
        ).inc()
        
        REQUEST_COUNT.labels(
            endpoint=request.url.path,
            method=request.method,
            status_bucket="4xx",
            model_version=model_version,
            release_track=release_track,
        ).inc()

        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )