from typing import Optional
from pydantic import BaseModel

class RequestPayload(BaseModel):
    feature1: float
    feature2: float
    request_id: Optional[str] = None