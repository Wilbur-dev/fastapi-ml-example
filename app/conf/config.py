from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_version: str = os.getenv("APP_VERSION", "dev").strip()
    model_uri: str = os.getenv("MODEL_URI", "").strip()
    model_path: str = os.getenv("MODEL_PATH", "").strip()
    model_stage: str = os.getenv("MODEL_STAGE", "unknown").strip()
    log_level: str = os.getenv("LOG_LEVEL", "INFO").strip()
    request_schema_version: str = os.getenv("REQUEST_SCHEMA_VERSION", "v1").strip()
    release_track: str = os.getenv("RELEASE_TRACK", "stable").strip()
    image_tag: str = os.getenv("IMAGE_TAG", "unknown").strip()


settings = Settings()