from app.api.schemas.payloads import RequestPayload

class InferenceService:
    def __init__(self, runtime):
        self.runtime = runtime
        
    
    def preprocess(self, payload: RequestPayload) -> list[list[float]]:
        return [[payload.feature1, payload.feature2]]

    def postprocess(self, payload: RequestPayload, prediction: int, probability: list[float]) -> dict:
        return {
            "prediction": int(prediction),
            "probability": probability,
            "model_version": self.runtime.model_version,
            "request_id": payload.request_id,
        }


    def predict(self, payload):
        
        features = self.preprocess(payload)
        prediction, probability = self.runtime.predict(features)
        return self.postprocess(payload, prediction, probability)
        
        