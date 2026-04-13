import joblib
import os
from os import getenv

def load_model():
    path = getenv("MODEL_PATH", "")
    if not path:
        raise RuntimeError("MODEL_PATH not set")
    
    if not os.path.exists(path):
        raise RuntimeError(f"Model file not found: {path}")

    model = joblib.load(path)
    return model, path