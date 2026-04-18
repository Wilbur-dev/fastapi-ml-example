from pydantic import BaseModel

class VersionResult(BaseModel):
    app_version: str
    model_version: str
    model_uri: str
    model_stage: str
    release_track: str
    loaded_at: str