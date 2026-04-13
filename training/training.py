from loguru import logger
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from joblib import dump
import mlflow
import mlflow.sklearn

from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "lr_model.joblib"


def train_model():
    '''train LR model using generated data and log to MLflow.'''
    
    mlflow.set_experiment("fastapi-ml-example")
    
    with mlflow.start_run(run_name="lr_baseline_v1"):
        # 1) 参数
        n_samples = 100
        centers = 2
        n_features = 2
        random_state = 0
        test_size = 0.30
        solver = "lbfgs"
        
        mlflow.log_param("n_samples", n_samples)
        mlflow.log_param("centers", centers)
        mlflow.log_param("n_features", n_features)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("test_size", test_size)
        mlflow.log_param("solver", solver)
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("version", "v1")
        
        # 2) 数据
        X, y = make_blobs(
            n_samples=n_samples,
            centers=centers,
            n_features=n_features,
            random_state=random_state,
        )
        logger.debug("data.shape: {}", X.shape)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # 3) 模型训练
        clf = LogisticRegression(solver=solver)

        start_time = time.perf_counter()
        clf.fit(X_train, y_train)
        train_time_ms = (time.perf_counter() - start_time) * 1000
        
        # 4) 指标
        accuracy = clf.score(X_test, y_test)
        logger.debug("Accuracy: {}", accuracy)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("train_time_ms", train_time_ms)

        # 5) 保存本地模型
        dump(clf, MODEL_PATH)
        logger.debug("Saved model to {}", MODEL_PATH)

        # 6) 记录 artifact
        mlflow.log_artifact(str(MODEL_PATH))

        # 7) 记录 MLflow model
        mlflow.sklearn.log_model(clf, artifact_path="model")

        logger.info("MLflow run completed successfully.")



if __name__ == '__main__':
    logger.debug("Training LR model")
    train_model()

