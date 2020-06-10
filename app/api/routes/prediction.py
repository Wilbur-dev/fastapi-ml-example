
from fastapi import APIRouter

from app.models.payloads import RequestPayload
from app.models.prediction import PredictionResult
#from app.conf.config import MODEL_PATH
from os import getenv
import joblib


router = APIRouter()

MODEL_PATH = getenv("MODEL_PATH", "")

clf = joblib.load(MODEL_PATH)


@router.post("/predict", response_model=PredictionResult, name="predict")
def post_predict(payload: RequestPayload = None) -> PredictionResult:

    if payload is None:
        raise ValueError("Invalid payload")

    x = [[payload.feature1, payload.feature2]]

    y = clf.predict(x)[0]
    prob = clf.predict_proba(x)[0].tolist()

    pred = PredictionResult(label=y, probability=prob)

    return pred