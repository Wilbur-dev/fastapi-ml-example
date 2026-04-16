import argparse
from training.config import load_config
from typing import Any


def str_to_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value

    normalized = value.lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


def build_parser(defaults: dict[str, Any]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train and register ML model")

    parser.add_argument(
        "--config",
        type=str,
        default="training/config.yaml",
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--experiment-name",
        type=str,
        default=defaults.get("experiment_name", "default-exp"),
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=defaults.get("run_name", "baseline"),
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=defaults.get("random_state", 42),
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=defaults.get("test_size", 0.2),
    )
    parser.add_argument(
        "--solver",
        type=str,
        default=defaults.get("solver", "liblinear"),
    )
    parser.add_argument(
        "--artifact-path",
        type=str,
        default=defaults.get("artifact_path", "model"),
    )
    parser.add_argument(
        "--register-model-name",
        type=str,
        default=defaults.get("register_model_name", "model"),
    )
    parser.add_argument(
        "--register-model",
        type=str_to_bool,
        default=defaults.get("register_model", True),
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=defaults.get("model_name", "logistic_regression"),
    )
    parser.add_argument(
        "--business-scenario",
        type=str,
        default=defaults.get("business_scenario", "unknown"),
    )
    parser.add_argument(
        "--request-schema-version",
        type=str,
        default=defaults.get("request_schema_version", "unknown"),
    )
    parser.add_argument(
        "--feature-schema-version",
        type=str,
        default=defaults.get("feature_schema_version", "unknown"),
    )

    return parser


def parse_args() -> tuple[argparse.Namespace, dict[str, Any]]:
    bootstrap_parser = argparse.ArgumentParser(add_help=False)
    bootstrap_parser.add_argument(
        "--config",
        type=str,
        default="training/config.yaml",
    )
    bootstrap_args, _ = bootstrap_parser.parse_known_args()

    config = load_config(bootstrap_args.config)
    parser = build_parser(config)
    args = parser.parse_args()

    return args, config