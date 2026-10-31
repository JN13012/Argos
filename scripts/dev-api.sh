#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

exec uv run --project "$repo_root" uvicorn argos.backend.api.main:app \
  --host "${ARGOS_API_HOST:-127.0.0.1}" \
  --port "${ARGOS_API_PORT:-8000}" \
  --reload
