from pydantic import BaseModel

class VersionResult(BaseModel):
    app_version: str
    model_version: str
    model_path: str