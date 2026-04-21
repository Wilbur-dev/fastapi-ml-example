#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
  docker compose stop api >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "==> Running lint"
docker compose build trainer
docker compose run --rm trainer ruff check .

echo "==> Running tests"
docker compose build api
docker compose run --rm api pytest -q

echo "==> Running training pipeline"
docker compose run --rm trainer python3 -m training.training --config training/config.yaml --register-model false --random-state 123

echo "==> promoting model to deployment artifact"
#docker compose run --rm trainer python3 scripts/promote_model.py
docker compose run --rm trainer python3 scripts/promote_model.py --update-env --model-stage production

echo "==> Checking metadata exists"
test -f "$ROOT_DIR/artifacts/metadata/latest_model_metadata.json"

echo "==> Checking deployment artifact exists"
test -d "$ROOT_DIR/deployment_mlruns/served_model"

echo "==> Checking promotion metadata exists"
test -f "$ROOT_DIR/deployment_mlruns/promotion_metadata.json"

echo "==> Starting API for smoke check"
docker compose up -d api

cleanup() {
  docker compose stop api >/dev/null 2>&1 || true
}
trap cleanup EXIT

sleep 15

echo "==> Checking /health"
curl -f http://127.0.0.1:8000/health

echo
echo "==> Checking /version"
curl -f http://127.0.0.1:8000/version

echo
echo "==> Checking /predict"
curl -f -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature1": 1.0, "feature2": 2.0, "request_id": "smoke-001"}'

echo
echo "==> local quality gate passed"