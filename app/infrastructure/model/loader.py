import joblib
import os
from os import getenv
import mlflow.sklearn

def load_model():
    model_uri = getenv("MODEL_URI", "").strip()
    model_path = getenv("MODEL_PATH", "").strip()
    
    
    if model_uri:
        model = mlflow.sklearn.load_model(model_uri)
        return model, model_uri
    
    if not model_path:
        raise RuntimeError("MODEL_PATH not set")
    
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model file not found: {model_path}")

    model = joblib.load(model_path)
    return model, model_path