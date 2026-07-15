#!/usr/bin/env bash
# CEXAI tenant run-launcher -- brings up the 3 local apps with ONE command (Mac / Linux / WSL).
#   public_site   -> Next dev (NEXT_PUBLIC_FIXTURES=1) on :3000
#   dashboard_web -> Next dev on :3001
#   dashboard_api -> uvicorn on :8000 (only if the Python deps are installed)
# Drop this at the tenant repo root (next to apps/). Also works if it lives in /boot/.
# Apps run as background jobs; Ctrl-C stops them all (the final `wait` blocks until then).
set -eu

# --- Resolve repo root (the directory that contains apps/) ---
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" && pwd -P)
ROOT="$SCRIPT_DIR"
if [ ! -d "$ROOT/apps" ] && [ -d "$(dirname -- "$ROOT")/apps" ]; then
  ROOT=$(dirname -- "$ROOT")
fi

# --- Pre-flight: node + npm must be on PATH (both web apps need them) ---
for bin in node npm; do
  command -v "$bin" >/dev/null 2>&1 || {
    echo "[FAIL] '$bin' not found on PATH. Install Node.js 18.17+ (https://nodejs.org) and retry." >&2
    exit 1
  }
done

# --- public_site -> :3000 (fixtures on) ---
(
  cd "$ROOT/apps/public_site"
  [ -d node_modules ] || npm install
  NEXT_PUBLIC_FIXTURES=1 PORT=3000 npm run dev
) &

# --- dashboard_web -> :3001 ---
(
  cd "$ROOT/apps/dashboard_web"
  [ -d node_modules ] || npm install
  NEXT_PUBLIC_FIXTURES=1 NEXT_PUBLIC_TENANT=starter NEXT_PUBLIC_BRAND_NAME=starter PORT=3001 npm run dev
) &

# --- dashboard_api -> :8000 (only if uvicorn + fastapi import cleanly) ---
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python
if command -v "$PY" >/dev/null 2>&1 && "$PY" -c "import uvicorn, fastapi" >/dev/null 2>&1; then
  (
    cd "$ROOT"
    "$PY" -m uvicorn apps.dashboard_api.main:app --port 8000 --reload
  ) &
else
  echo "[i] dashboard_api skipped -- Python deps not installed. To enable the API:"
  echo "      pip install -r apps/dashboard_api/requirements.txt"
  echo "      $PY -m uvicorn apps.dashboard_api.main:app --port 8000 --reload"
fi

echo ""
echo "Site http://localhost:3000/t/starter | Admin http://localhost:3001 | API http://localhost:8000"
wait
