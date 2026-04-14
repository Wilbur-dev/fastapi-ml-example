from loguru import logger
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from joblib import dump
import mlflow
import mlflow.sklearn

from pathlib import Path
import time

import argparse

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "lr_model.joblib"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-name", type=str, default="lr_baseline_v1")
    parser.add_argument("--random-state", type=int, default=0)
    parser.add_argument("--test-size", type=float, default=0.30)
    parser.add_argument("--solver", type=str, default="lbfgs")
    parser.add_argument("--register-model", action="store_true")
    return parser.parse_args()


def train_model(args):
    '''train LR model using generated data and log to MLflow.'''
    
    mlflow.set_experiment("fastapi-ml-example")
    
    with mlflow.start_run(run_name=args.run_name) as run:
        # 1) 参数
        n_samples = 100
        centers = 2
        n_features = 2
        random_state = args.random_state
        test_size = args.test_size
        solver = args.solver
        
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
        
        # 模型大小
        model_size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
        mlflow.log_metric("model_size_mb", model_size_mb)
        
        # 单次推理延迟
        sample = X_test[:1]

        start_pred = time.perf_counter()
        _ = clf.predict(sample)
        single_request_latency_ms = (time.perf_counter() - start_pred) * 1000
        mlflow.log_metric("single_request_latency_ms", single_request_latency_ms)
        logger.debug("model_size_mb: {}", model_size_mb)
        logger.debug("single_request_latency_ms: {}", single_request_latency_ms)

        # 6) 记录 artifact
        mlflow.log_artifact(str(MODEL_PATH))

        # 7) 记录 MLflow model
        mlflow.sklearn.log_model(clf, artifact_path="model")
        run_id = run.info.run_id
        
        if args.register_model:
            model_uri = f"runs:/{run_id}/model"
            result = mlflow.register_model(
                model_uri=model_uri,
                name="fastapi_ml_classifier"
            )
            logger.info("Registered model: name={}, version={}", result.name, result.version)
        mlflow.log_param("logged_model_uri", f"runs:/{run_id}/model")
        
        logger.info("MLflow run completed successfully.")



if __name__ == '__main__':
    logger.debug("Training LR model")
    args = parse_args()
    train_model(args)

