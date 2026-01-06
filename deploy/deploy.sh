#!/usr/bin/env bash
set -euo pipefail

DEPLOY_DIR="/opt/onlinelearning"
COMPOSE_FILE="docker-compose.prod.yaml"
ENV_FILE=".env.docker"

cd "$DEPLOY_DIR"

echo "[1/8] Preflight"
test -f "$COMPOSE_FILE" || { echo "Missing $COMPOSE_FILE"; exit 1; }
test -f "$ENV_FILE" || { echo "Missing $DEPLOY_DIR/$ENV_FILE"; exit 1; }

echo "[2/8] Convert CRLF->LF for nginx.conf if needed"
if command -v sed >/dev/null 2>&1; then
  sed -i 's/\r$//' "$DEPLOY_DIR/nginx/nginx.conf" || true
fi

echo "[3/8] Build app images locally (no GHCR)"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --pull

echo "[4/8] Start infra"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d db redis

echo "[5/8] Run migrations (one-shot)"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up --no-deps --abort-on-container-exit migrate

echo "[6/8] Start/Update app stack"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --remove-orphans web celery celery_beat nginx

echo "[7/8] Cleanup dangling images (safe)"
docker image prune -f || true

echo "[8/8] Status"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps