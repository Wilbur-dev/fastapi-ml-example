from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

METRIC_LABELS = ["endpoint", "method", "status_bucket", "model_version", "release_track"]

REQUEST_COUNT = Counter(
    "inference_request_total",
    "Total number of inference requests",
    METRIC_LABELS,
)

ERROR_COUNT = Counter(
    "inference_error_total",
    "Total number of failed inference requests grouped by status bucket",
    METRIC_LABELS,
)

LATENCY = Histogram(
    "inference_latency_seconds",
    "Inference latency in seconds",
    ["endpoint", "method", "model_version", "release_track"],
)

def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)