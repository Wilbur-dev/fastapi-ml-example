class InferenceService:
    def __init__(self, runtime):
        self.runtime = runtime

    def predict(self, payload):
        # 👉 以后这里可以换成 text → vector
        features = [[payload.feature1, payload.feature2]]

        y, prob = self.runtime.predict(features)

        return {
            #"label": y,
            #"probability": prob,
            #"model_version": self.runtime.model_version
            
            "prediction": int(y),
            "probability": prob,
            "model_version": self.runtime.model_version,
            "request_id": payload.request_id,
        }