#!/usr/bin/env bash
# Boots the Leven API (FastAPI/uvicorn) for local development.
#
# - Ensures a working Python virtualenv exists (recreates it if it's
#   missing or broken, e.g. copied from a machine with a different
#   architecture).
# - Installs/updates Python dependencies.
# - Ensures Postgres is running and that the role/database referenced by
#   DATABASE_URL in .env exist.
# - Runs Alembic migrations.
# - Starts uvicorn with --reload.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log() { printf '[api] %s\n' "$1"; }

# ---------------------------------------------------------------------------
# 1. Virtualenv
# ---------------------------------------------------------------------------
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python"

venv_is_healthy() {
  [ -x "$PYTHON_BIN" ] && "$PYTHON_BIN" -c "import sys" >/dev/null 2>&1
}

if ! venv_is_healthy; then
  log "Creating virtualenv..."
  rm -rf "$VENV_DIR"
  command -v python3 >/dev/null 2>&1 || { log "python3 not found. Install Python 3 first."; exit 1; }
  python3 -m venv "$VENV_DIR"
fi

log "Installing Python dependencies..."
"$PYTHON_BIN" -m pip install --upgrade pip -q
"$PYTHON_BIN" -m pip install -r requirements.txt -q

# ---------------------------------------------------------------------------
# 2. Load .env
# ---------------------------------------------------------------------------
if [ ! -f .env ]; then
  log ".env not found, copying from .env.example"
  cp .env.example .env
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

DATABASE_URL="${DATABASE_URL:-postgresql://leven:leven@localhost:5432/leven}"

# ---------------------------------------------------------------------------
# 3. Ensure Postgres is running
# ---------------------------------------------------------------------------
ensure_postgres_running() {
  if command -v pg_isready >/dev/null 2>&1 && pg_isready -q -h localhost -p 5432 2>/dev/null; then
    return 0
  fi

  if command -v brew >/dev/null 2>&1; then
    local pg_service
    pg_service=$(brew list --formula 2>/dev/null | grep -m1 '^postgresql')
    if [ -n "$pg_service" ]; then
      log "Starting Postgres (brew services start $pg_service)..."
      brew services start "$pg_service" >/dev/null
      for _ in $(seq 1 10); do
        pg_isready -q -h localhost -p 5432 2>/dev/null && return 0
        sleep 1
      done
    fi
  fi

  log "Postgres does not appear to be running and could not be started automatically."
  log "Start it manually, then re-run this script."
  exit 1
}

ensure_postgres_running

# ---------------------------------------------------------------------------
# 4. Ensure role + database exist (idempotent), parsed from DATABASE_URL
# ---------------------------------------------------------------------------
# DATABASE_URL format: postgresql://USER:PASSWORD@HOST:PORT/DBNAME
url="${DATABASE_URL#postgresql://}"
db_user="${url%%:*}"
rest="${url#*:}"
db_pass="${rest%%@*}"
rest="${rest#*@}"
db_host="${rest%%:*}"
rest="${rest#*:}"
db_port="${rest%%/*}"
db_name="${rest#*/}"

ensure_role_and_db() {
  if ! psql -h "$db_host" -p "$db_port" -U "$(whoami)" -d postgres -tAc \
      "SELECT 1 FROM pg_roles WHERE rolname='$db_user'" 2>/dev/null | grep -q 1; then
    log "Creating Postgres role '$db_user'..."
    psql -h "$db_host" -p "$db_port" -U "$(whoami)" -d postgres -c \
      "CREATE ROLE \"$db_user\" WITH LOGIN PASSWORD '$db_pass';" >/dev/null
  fi

  if ! psql -h "$db_host" -p "$db_port" -U "$(whoami)" -d postgres -tAc \
      "SELECT 1 FROM pg_database WHERE datname='$db_name'" 2>/dev/null | grep -q 1; then
    log "Creating Postgres database '$db_name'..."
    psql -h "$db_host" -p "$db_port" -U "$(whoami)" -d postgres -c \
      "CREATE DATABASE \"$db_name\" OWNER \"$db_user\";" >/dev/null
  fi
}

if command -v psql >/dev/null 2>&1; then
  ensure_role_and_db
else
  log "psql not found; skipping automatic role/database creation."
fi

# ---------------------------------------------------------------------------
# 5. Migrations
# ---------------------------------------------------------------------------
log "Running Alembic migrations..."
"$PYTHON_BIN" -m alembic upgrade head

# ---------------------------------------------------------------------------
# 6. Start the server
# ---------------------------------------------------------------------------
log "Starting uvicorn on http://0.0.0.0:8000 ..."
exec "$PYTHON_BIN" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
