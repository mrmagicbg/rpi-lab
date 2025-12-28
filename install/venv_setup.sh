#!/usr/bin/env bash
# Create a Python virtualenv for the RPI Lab and install requirements
set -euo pipefail

VENV_DIR="/opt/rpi-lab/.venv"
REQ_FILE="/opt/rpi-lab/requirements.txt"

if [ "$EUID" -ne 0 ]; then
  echo "Warning: running as non-root. The venv will be created in $PWD unless you run with sudo."
fi

echo "[venv_setup] Installing system dependencies..."
apt-get update -y || true
apt-get install -y python3-full python3-dev build-essential || true

echo "[venv_setup] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if [ -f "$REQ_FILE" ]; then
  echo "[venv_setup] Upgrading pip..."
  pip install --upgrade pip -q
  
  echo "[venv_setup] Installing Python packages from requirements.txt..."
  pip install -r "$REQ_FILE" -q
  
  echo "[venv_setup] ✓ All packages installed successfully"
else
  echo "No requirements file found at $REQ_FILE; virtualenv created but nothing installed."
fi

echo "[venv_setup] ✓ Virtualenv ready at $VENV_DIR"
echo "[venv_setup] To activate: source $VENV_DIR/bin/activate"
