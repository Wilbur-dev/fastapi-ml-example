from pydantic import BaseModel

class VersionResult(BaseModel):
    app_version: str
    model_version: str
    model_uri: str
    model_stage: str
    loaded_at: str