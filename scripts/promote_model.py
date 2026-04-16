from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METADATA_PATH = ROOT / "artifacts" / "metadata" / "latest_model_metadata.json"
ENV_PATH = ROOT / ".env"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote model URI to service .env")
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


def main() -> None:
    args = parse_args()

    if args.model_uri:
        model_uri = args.model_uri
    else:
        metadata = load_metadata(Path(args.metadata_path))
        model_uri = metadata["model_uri"]
        
    if args.model_stage:
        model_stage = args.model_stage
    elif metadata and "model_stage" in metadata:
        model_stage = metadata["model_stage"]
    else:
        model_stage = "promoted"


    update_env_file(
        env_path=ENV_PATH,
        model_uri=model_uri,
        model_stage=model_stage
    )

    print(f"Promoted MODEL_URI -> {model_uri}")
    print(f"Updated .env at: {ENV_PATH}")


if __name__ == "__main__":
    main()