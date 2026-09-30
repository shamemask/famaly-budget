#!/usr/bin/env sh
# Bootstraps the Python toolchain (uv -> project deps) if missing, then starts
# the Django dev server. Used by `pnpm dev` so the preview works in a fresh
# sandbox where uv is not on PATH.
set -eu

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  echo "[dev] installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null
fi

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
fi

echo "[dev] syncing python dependencies..."
uv sync

echo "[dev] applying migrations..."
uv run python manage.py migrate --noinput

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
exec uv run python manage.py runserver "$HOST:$PORT"
