import joblib
import os
import mlflow.sklearn
from app.conf.config import settings

def load_model():
    model_uri = settings.model_uri
    model_path = settings.model_path
    
    
    if model_uri:
        try:
            model = mlflow.sklearn.load_model(model_uri)
            return model, model_uri
        except Exception as e:
            raise RuntimeError(f"Failed to load model from MODEL_URI={model_uri}: {e}")
    
    if not model_path:
        raise RuntimeError("MODEL_PATH not set")
    
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model file not found: {model_path}")

    try:
        model = joblib.load(model_path)
        return model, model_path
    except Exception as e:
        raise RuntimeError(f"Failed to load model from MODEL_PATH={model_path}: {e}")