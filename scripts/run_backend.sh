#!/usr/bin/env sh
set -eu

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$PROJECT_ROOT/backend"

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port "${BACKEND_PORT:-8000}"
