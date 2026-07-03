#!/usr/bin/env bash
set -e

echo "SimpleDL Bootstrap (Unix/macOS)"

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON=python

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "[ERROR] Python not found. Install Python 3.10+."
  exit 1
fi

echo "[STEP 1] Python OK"

cd "$(dirname "$0")/.."

USE_VENV=${1:-}

if [ -z "$USE_VENV" ]; then
  read -p "Use virtualenv? [Y/n]: " yn
  case "$yn" in
    [Nn]*) USE_VENV=false ;;
    *) USE_VENV=true ;;
  esac
fi

if [ "$USE_VENV" = true ]; then
  echo "[STEP 2] Creating venv..."
  $PYTHON -m venv .venv

  echo "[STEP 3] Activating venv..."
  source .venv/bin/activate
fi

echo "[STEP 4] Upgrading pip..."
$PYTHON -m pip install -U pip

echo "[STEP 5] Installing requirements..."
pip install -r requirements.txt

echo "[STEP 6] Checking FFmpeg..."
command -v ffmpeg >/dev/null 2>&1 || echo "[WARNING] FFmpeg not found"

echo "[STEP 7] Checking yt-dlp..."
$PYTHON -c "import yt_dlp" >/dev/null 2>&1 || echo "[WARNING] yt-dlp missing"

echo "Bootstrap complete"
echo "Run: python src/main.py"