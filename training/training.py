from __future__ import annotations

import argparse
from pathlib import Path

import time
from typing import Any

import mlflow
import mlflow.sklearn
from loguru import logger
from sklearn.linear_model import LogisticRegression

from training.parser import parse_args
from training.utils.seed import set_seed
from training.dataset_process import generate_dataset, split_dataset
from training.mlflow_logger import log_training_params, log_training_metrics, log_model
from training.model_saver_register import save_local_model, mlflow_register_model

import json
from datetime import datetime, UTC


ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "lr_model.joblib"
METADATA_PATH = ROOT / "artifacts" / "metadata" / "latest_model_metadata.json"



def build_model(solver: str, random_state: int) -> LogisticRegression:
    return LogisticRegression(
        solver=solver,
        random_state=random_state,
    )


def train_classifier(
    X_train: Any,
    y_train: Any,
    solver: str,
    random_state: int,
) -> tuple[LogisticRegression, float]:
    model = build_model(solver=solver, random_state=random_state)

    start_time = time.perf_counter()
    model.fit(X_train, y_train)
    train_time_ms = (time.perf_counter() - start_time) * 1000

    return model, train_time_ms


def evaluate_classifier(model: LogisticRegression, X_test: Any, y_test: Any) -> dict[str, float]:
    accuracy = model.score(X_test, y_test)

    sample = X_test[:1]
    start_pred = time.perf_counter()
    _ = model.predict(sample)
    single_request_latency_ms = (time.perf_counter() - start_pred) * 1000

    return {
        "accuracy": accuracy,
        "single_request_latency_ms": single_request_latency_ms,
    }

def write_model_metadata(
    output_path: Path,
    run_id: str,
    model_uri: str,
    metrics: dict[str, float],
    register_model_name: str,
    model_stage: str,
) -> None:
    payload = {
        "run_id": run_id,
        "model_uri": model_uri,
        "offline_metrics": {
            "accuracy": metrics.get("accuracy"),
        },
        "serving_metrics": {
            "single_request_latency_ms": metrics.get("single_request_latency_ms"),
        },
        "chosen_reason": "Selected as latest candidate model based on current training run metrics.",

        "register_model_name": register_model_name,
        "model_stage": model_stage,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def train_model(args: argparse.Namespace) -> None:
    set_seed(args.random_state)
    mlflow.set_experiment(args.experiment_name)

    with mlflow.start_run(run_name=args.run_name) as run:
        log_training_params(args)

        X, y = generate_dataset(random_state=args.random_state)
        X_train, X_test, y_train, y_test = split_dataset(
            X=X,
            y=y,
            test_size=args.test_size,
            random_state=args.random_state,
        )

        model, train_time_ms = train_classifier(
            X_train=X_train,
            y_train=y_train,
            solver=args.solver,
            random_state=args.random_state,
        )

        metrics = evaluate_classifier(model=model, X_test=X_test, y_test=y_test)
        model_size_mb = save_local_model(model=model, model_path=MODEL_PATH)

        log_training_metrics(
            metrics=metrics,
            train_time_ms=train_time_ms,
            model_size_mb=model_size_mb,
        )

        logged_model_uri = f"runs:/{run.info.run_id}/{args.artifact_path}"
        log_model(
            model=model,
            artifact_path=args.artifact_path,
            logged_model_uri=logged_model_uri,
            model_path=MODEL_PATH
        )
        
        mlflow_register_model(
        	register_model=args.register_model, 
        	logged_model_uri=logged_model_uri, 
        	register_model_name=args.register_model_name
        )
        
        write_model_metadata(
            output_path=METADATA_PATH,
            run_id=run.info.run_id,
            model_uri=logged_model_uri,
            metrics=metrics,
            register_model_name=args.register_model_name,
            model_stage="candidate"
        )

        logger.info("Accuracy: {}", metrics["accuracy"])
        logger.info("Train time (ms): {}", train_time_ms)
        logger.info("Model size (MB): {}", model_size_mb)
        logger.info(
            "Single request latency (ms): {}",
            metrics["single_request_latency_ms"],
        )
        logger.info("MLflow run completed successfully.")


def main() -> None:
    args, _ = parse_args()
    train_model(args)


if __name__ == "__main__":
    main()