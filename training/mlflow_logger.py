from training.dataset_process import get_dataset_params
import mlflow
import argparse
from sklearn.linear_model import LogisticRegression
from pathlib import Path

def log_training_params(args: argparse.Namespace) -> None:
    dataset_params = get_dataset_params()

    mlflow.log_param("n_samples", dataset_params["n_samples"])
    mlflow.log_param("centers", dataset_params["centers"])
    mlflow.log_param("n_features", dataset_params["n_features"])
    mlflow.log_param("random_state", args.random_state)
    mlflow.log_param("test_size", args.test_size)
    mlflow.log_param("solver", args.solver)
    mlflow.log_param("model_type", "LogisticRegression")
    mlflow.log_param("experiment_name", args.experiment_name)
    mlflow.log_param("model_name", args.model_name)
    mlflow.log_param("business_scenario", args.business_scenario)
    mlflow.log_param("request_schema_version", args.request_schema_version)
    mlflow.log_param("feature_schema_version", args.feature_schema_version)


def log_training_metrics(metrics: dict[str, float], train_time_ms: float, model_size_mb: float) -> None:
    mlflow.log_metric("accuracy", metrics["accuracy"])
    mlflow.log_metric("train_time_ms", train_time_ms)
    mlflow.log_metric("model_size_mb", model_size_mb)
    mlflow.log_metric("single_request_latency_ms", metrics["single_request_latency_ms"])


def log_model(
    model: LogisticRegression,
    artifact_path: str,
    logged_model_uri: str, 
    model_path: Path
) -> None:
    mlflow.log_artifact(str(model_path))
    mlflow.sklearn.log_model(model, artifact_path=artifact_path)

    mlflow.log_param("logged_model_uri", logged_model_uri)