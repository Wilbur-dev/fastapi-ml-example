from typing import List, Optional
from pydantic import BaseModel

class PredictionResult(BaseModel):
    prediction: int
    probability: List[float]
    model_version: str
    request_id: Optional[str] = None
