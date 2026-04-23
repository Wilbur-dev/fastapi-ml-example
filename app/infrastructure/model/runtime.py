from datetime import datetime, UTC
from app.conf.config import settings

class ModelRuntime:
    def __init__(self, model, model_uri: str):
        self.model = model
        self.model_uri = model_uri
        self.model_stage = settings.model_stage
        self.app_version = settings.app_version
        self.release_track = settings.release_track
        self.loaded_at = datetime.now(UTC).isoformat()
        self.image_tag = settings.image_tag
        if settings.model_version:
            self.model_version = settings.model_version
        elif model_uri.startswith("models:/"):
            self.model_version = model_uri.rstrip("/").split("/")[-1]
        elif model_uri.startswith("runs:/"):
            self.model_version = "run-artifact"
        else:
            self.model_version = "unknown-model"

    def predict(self, features):
        y = self.model.predict(features)[0]
        prob = self.model.predict_proba(features)[0].tolist()
        return y, prob