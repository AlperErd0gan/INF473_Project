#!/usr/bin/env bash
# Render start script — not used by run.sh (local dev unchanged)
set -euo pipefail

cd backend
exec uvicorn main_render:app --host 0.0.0.0 --port "${PORT:-8000}"
