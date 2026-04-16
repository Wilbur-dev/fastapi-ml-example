
import mlflow
from joblib import dump
from loguru import logger
from sklearn.linear_model import LogisticRegression
from pathlib import Path





def save_local_model(
    model: LogisticRegression, 
    model_path: Path
) -> float:
    dump(model, model_path)
    logger.debug("Saved model to {}", model_path)

    model_size_mb = model_path.stat().st_size / (1024 * 1024)
    return model_size_mb


def mlflow_register_model(
	register_model: bool,
	logged_model_uri: str,
    register_model_name: str
):
    if register_model:
        result = mlflow.register_model(
            model_uri=logged_model_uri,
            name=register_model_name,
        )
        logger.info(
            "Registered model: name={}, version={}",
            result.name,
            result.version,
        )
