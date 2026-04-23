from time import perf_counter
from fastapi import APIRouter, Request, HTTPException

from app.api.schemas.payloads import RequestPayload
from app.api.schemas.prediction import PredictionResult
from app.observability.metrics import REQUEST_COUNT, ERROR_COUNT, LATENCY
from loguru import logger


router = APIRouter()


@router.post("/predict", response_model=PredictionResult, name="predict")
def post_predict(payload: RequestPayload, request: Request):

    service = request.app.state.inference_service
    runtime = service.runtime

    endpoint = "/predict"
    method = "POST"
    model_version = runtime.model_version
    release_track = runtime.release_track

    start = perf_counter()
    status_bucket = "2xx"
        
    try:
        result = service.predict(payload)
        return PredictionResult(**result)
    
    except ValueError as e: # RequestValidationError Handler already handles this
        status_bucket = "4xx"
        ERROR_COUNT.labels(
            endpoint=endpoint,
            method=method,
            status_bucket=status_bucket,
            model_version=model_version,
            release_track=release_track,
        ).inc()
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception:
        status_bucket = "5xx"
        ERROR_COUNT.labels(
            endpoint=endpoint,
            method=method,
            status_bucket=status_bucket,
            model_version=model_version,
            release_track=release_track,
        ).inc()
        raise HTTPException(status_code=500, detail="prediction failed")

    finally:
        elapsed = perf_counter() - start

        REQUEST_COUNT.labels(
            endpoint=endpoint,
            method=method,
            status_bucket=status_bucket,
            model_version=model_version,
            release_track=release_track,
        ).inc()

        LATENCY.labels(
            endpoint=endpoint,
            method=method,
            model_version=model_version,
            release_track=release_track,
        ).observe(elapsed)
        
        logger.info(
            "predict request_id={} endpoint={} method={} status_bucket={} model_version={} release_track={} latency_ms={:.2f}",
            payload.request_id,
            endpoint,
            method,
            status_bucket,
            model_version,
            release_track,
            elapsed * 1000,
        )
        