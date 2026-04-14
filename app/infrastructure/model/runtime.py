import os

from datetime import datetime, UTC

class ModelRuntime:
    def __init__(self, model, model_uri: str):
        self.model = model
        self.model_uri = model_uri
        self.model_stage = os.getenv("MODEL_STAGE", "unknown")
        self.app_version = os.getenv("APP_VERSION", "unknown")
        self.loaded_at = datetime.now(UTC).isoformat()
        if model_uri.startswith("models:/"):
            self.model_version = model_uri.rstrip("/").split("/")[-1]
        else:
            self.model_version = "unknown"

    def predict(self, features):
        y = self.model.predict(features)[0]
        prob = self.model.predict_proba(features)[0].tolist()
        return y, prob