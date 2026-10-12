#!/usr/bin/env bash
#
# Start the FastAPI backend (port 8000) and the Vite dashboard (port
# 5173) together. Press Ctrl+C once to stop both.
#
# Usage:
#   ./dev.sh            # install deps if needed, then run both
#   ./dev.sh --no-install   # skip dependency checks (faster restart)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$ROOT_DIR/server"
DASHBOARD_DIR="$ROOT_DIR/dashboard"

INSTALL=1
[[ "${1:-}" == "--no-install" ]] && INSTALL=0

# Prefer the project virtualenv's Python if it exists.
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON="$ROOT_DIR/.venv/bin/python"
elif [[ -x "$SERVER_DIR/.venv/bin/python" ]]; then
  PYTHON="$SERVER_DIR/.venv/bin/python"
else
  PYTHON="python3"
fi

echo "Using Python: $PYTHON"

if [[ "$INSTALL" == "1" ]]; then
  echo "==> Installing backend dependencies"
  "$PYTHON" -m pip install -q -r "$SERVER_DIR/requirements.txt"

  if [[ ! -d "$DASHBOARD_DIR/node_modules" ]]; then
    echo "==> Installing frontend dependencies"
    (cd "$DASHBOARD_DIR" && npm install)
  fi
fi

# Track child PIDs so we can clean up on exit.
PIDS=()

cleanup() {
  echo ""
  echo "==> Shutting down..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  echo "==> Stopped."
}
trap cleanup INT TERM EXIT

echo "==> Starting backend  : http://localhost:8000"
(cd "$SERVER_DIR" && "$PYTHON" -m uvicorn app.main:app --reload --port 8000) &
PIDS+=($!)

echo "==> Starting frontend : http://localhost:5173"
(cd "$DASHBOARD_DIR" && npm run dev) &
PIDS+=($!)

echo ""
echo "Both running. Open http://localhost:5173  (Ctrl+C to stop)"
echo ""

# Portable wait: macOS ships bash 3.2 which has no `wait -n`, so poll
# the children and let the cleanup trap stop the survivor if one dies.
while true; do
  for pid in "${PIDS[@]}"; do
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "==> A process exited; stopping the other."
      exit 1
    fi
  done
  sleep 1
done
