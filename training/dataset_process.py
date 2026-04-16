from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from loguru import logger
from typing import Any

def get_dataset_params() -> dict[str, int]:
    return {
        "n_samples": 100,
        "centers": 2,
        "n_features": 2,
    }


def generate_dataset(random_state: int) -> tuple[Any, Any]:
    params = get_dataset_params()
    X, y = make_blobs(
        n_samples=params["n_samples"],
        centers=params["centers"],
        n_features=params["n_features"],
        random_state=random_state,
    )
    logger.debug("Generated dataset with shape={}", X.shape)
    return X, y


def split_dataset(X: Any, y: Any, test_size: float, random_state: int):
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
    )