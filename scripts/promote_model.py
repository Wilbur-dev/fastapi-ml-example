from __future__ import annotations

import argparse
import json
from pathlib import Path

import shutil
from datetime import datetime, timezone

import mlflow.sklearn


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METADATA_PATH = ROOT / "artifacts" / "metadata" / "latest_model_metadata.json"
ENV_PATH = ROOT / ".env"


DEPLOYMENT_MLRUNS_DIR = ROOT / "deployment_mlruns"
DEPLOYMENT_MODEL_DIR = DEPLOYMENT_MLRUNS_DIR / "served_model"
PROMOTION_METADATA_PATH = DEPLOYMENT_MLRUNS_DIR / "promotion_metadata.json"

DEPLOYMENT_MODEL_URI = "file:///app/deployment_mlruns/served_model"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a source MLflow model URI into a deployment-ready MLflow artifact."
    )
    parser.add_argument(
        "--metadata-path",
        type=str,
        default=str(DEFAULT_METADATA_PATH),
        help="Path to model metadata json",
    )
    parser.add_argument(
        "--model-uri",
        type=str,
        default="",
        help="Directly specify model URI; overrides metadata file",
    )
    parser.add_argument(
        "--model-stage",
        type=str,
        default=None,
        help="Value to write into MODEL_STAGE",
    )
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Also update local .env with deployment MODEL_URI",
    )
    return parser.parse_args()
    return parser.parse_args()


def load_metadata(metadata_path: Path) -> dict:
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    with metadata_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def update_env_file(env_path: Path, model_uri: str, model_stage: str) -> None:
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")

    lines = env_path.read_text(encoding="utf-8").splitlines()
    updated_lines = []
    seen_model_uri = False
    seen_model_stage = False

    for line in lines:
        if line.startswith("MODEL_URI="):
            updated_lines.append(f"MODEL_URI={model_uri}")
            seen_model_uri = True
        elif line.startswith("MODEL_STAGE="):
            updated_lines.append(f"MODEL_STAGE={model_stage}")
            seen_model_stage = True
        else:
            updated_lines.append(line)

    if not seen_model_uri:
        updated_lines.append(f"MODEL_URI={model_uri}")
    if not seen_model_stage:
        updated_lines.append(f"MODEL_STAGE={model_stage}")

    env_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def export_deployment_model(source_model_uri: str) -> None:
    print(f"Loading source model from: {source_model_uri}")
    model = mlflow.sklearn.load_model(source_model_uri)

    if DEPLOYMENT_MODEL_DIR.exists():
        shutil.rmtree(DEPLOYMENT_MODEL_DIR)

    DEPLOYMENT_MLRUNS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Saving deployment model to: {DEPLOYMENT_MODEL_DIR}")
    mlflow.sklearn.save_model(sk_model=model, path=str(DEPLOYMENT_MODEL_DIR))


def write_promotion_metadata(
    source_model_uri: str,
    model_stage: str,
    source_metadata: dict | None,
) -> None:
    payload = {
        "source_model_uri": source_model_uri,
        "deployment_model_uri": DEPLOYMENT_MODEL_URI,
        "model_stage": model_stage,
        "promoted_at": datetime.now(timezone.utc).isoformat(),
    }

    if source_metadata:
        payload["source_metadata"] = source_metadata

    PROMOTION_METADATA_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    metadata = None

    if args.model_uri:
        source_model_uri = args.model_uri
    else:
        metadata = load_metadata(Path(args.metadata_path))
        source_model_uri = metadata["model_uri"]
        
    if args.model_stage:
        model_stage = args.model_stage
    elif metadata and "model_stage" in metadata:
        model_stage = metadata["model_stage"]
    else:
        model_stage = "promoted"


    export_deployment_model(source_model_uri=source_model_uri)
    write_promotion_metadata(
        source_model_uri=source_model_uri,
        model_stage=model_stage,
        source_metadata=metadata,
    )
    
    if args.update_env:
        update_env_file(
            env_path=ENV_PATH,
            model_uri=DEPLOYMENT_MODEL_URI,
            model_stage=model_stage
        )
        print(f"Updated .env at: {ENV_PATH}")

    
    #print(f"Promoted MODEL_URI -> {model_uri}")
    #print(f"Updated .env at: {ENV_PATH}")
    print(f"Promoted source model -> {source_model_uri}")
    print(f"Deployment MODEL_URI -> {DEPLOYMENT_MODEL_URI}")
    print(f"Promotion metadata -> {PROMOTION_METADATA_PATH}")


if __name__ == "__main__":
    main()