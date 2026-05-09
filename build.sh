#!/usr/bin/env bash
# Render build script — not used by run.sh (local dev unchanged)
set -euo pipefail

echo "==> Installing backend dependencies"
pip install -r backend/requirements.txt aiofiles

echo "==> Patching api.js for same-origin Render deployment"
# Replace hardcoded localhost URL with empty string so fetch uses relative paths.
# This only affects the bundled output; the source file is restored after build.
cp frontend/src/api.js frontend/src/api.js.bak
sed 's|const BASE_URL = "http://localhost:8000"|const BASE_URL = ""|g' \
    frontend/src/api.js.bak > frontend/src/api.js

echo "==> Building frontend"
cd frontend
npm ci
npm run build
cd ..

echo "==> Restoring api.js"
mv frontend/src/api.js.bak frontend/src/api.js

echo "==> Copying dist into backend/static"
rm -rf backend/static
cp -r frontend/dist backend/static

echo "==> Build complete"
