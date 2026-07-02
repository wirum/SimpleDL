#!/usr/bin/env bash
set -e

echo "SimpleDL bootstrap (Unix/macOS)"
PYTHON=python3
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  PYTHON=python
fi

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Error: Python not found on PATH. Install Python 3 and re-run this script." >&2
  exit 1
fi

USE_VENV=${1:-}
if [ -z "$USE_VENV" ]; then
  read -p "Create and use a virtualenv? [Y/n]: " yn
  case "$yn" in
    [Nn]*) USE_VENV=false ;;
    *) USE_VENV=true ;;
  esac
fi

ROOT_DIR=$(pwd)
BOOTSTRAP_LOG="./logs/bootstrap.log"
mkdir -p "$(dirname "$BOOTSTRAP_LOG")"

# Start logging
{
  echo "=== SimpleDL Bootstrap Log ==="
  echo "Start time: $(date)"
  echo "System: $(uname -s) $(uname -m)"
  echo "Python: $PYTHON ($(python --version 2>&1))"
  echo "Working directory: $ROOT_DIR"
  echo ""
  echo "[STEP 1] Checking Python..."
  $PYTHON --version
  echo "[OK] Python available"
  echo ""

  if [ "$USE_VENV" = true ]; then
    echo "[STEP 2] Creating virtualenv .venv..."
    $PYTHON -m venv .venv
    echo "[OK] Virtualenv created"
    echo ""
    echo "[STEP 3] Activating virtualenv..."
    source .venv/bin/activate
    echo "[OK] Virtualenv activated"
    echo ""
    echo "[STEP 4] Upgrading pip..."
    pip install -U pip 2>&1 | tail -1
    echo "[OK] Pip upgraded"
    echo ""
    echo "[STEP 5] Installing requirements..."
    pip install -r requirements.txt
    echo "[OK] Requirements installed"
  else
    echo "[STEP 2] Installing requirements globally..."
    pip install -U pip 2>&1 | tail -1
    pip install -r requirements.txt
    echo "[OK] Requirements installed"
  fi
  echo ""

  echo "[STEP 6] Checking FFmpeg..."
  if command -v ffmpeg >/dev/null 2>&1; then
    echo "[OK] FFmpeg found: $(ffmpeg -version 2>&1 | head -1)"
  else
    echo "[WARNING] FFmpeg not found. Audio extraction/embedding may fail."
  fi
  echo ""

  echo "[STEP 7] Checking yt-dlp..."
  if python -c "import yt_dlp; print(yt_dlp.__version__)" 2>/dev/null; then
    echo "[OK] yt-dlp available"
  else
    echo "[ERROR] yt-dlp not installed in active environment"
  fi
  echo ""

  echo "End time: $(date)"
  echo "=== Bootstrap Complete ==="
} | tee "$BOOTSTRAP_LOG"

echo ""
echo "Bootstrap log saved to: $BOOTSTRAP_LOG"
echo "Next: Review config.example.yml and create config.yml if needed"
