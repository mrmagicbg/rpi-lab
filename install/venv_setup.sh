#!/usr/bin/env bash
# Create a Python virtualenv for the RPI Lab and install requirements
set -euo pipefail

VENV_DIR="/opt/rpi-lab/.venv"
REQ_FILE="/opt/rpi-lab/requirements.txt"

if [ "$EUID" -ne 0 ]; then
  echo "Warning: running as non-root. The venv will be created in $PWD unless you run with sudo."
fi

echo "[venv_setup] Installing system dependencies for DHT22 sensor..."
apt-get install -y python3-dev build-essential || true

echo "[venv_setup] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if [ -f "$REQ_FILE" ]; then
  echo "[venv_setup] Upgrading pip..."
  pip install --upgrade pip -q
  
  echo "[venv_setup] Installing Python packages..."
  pip install rich==13.3.0 loguru==0.7.0 evdev==1.9.2 -q
  
  # Install Adafruit_DHT with force-pi flag for Raspberry Pi
  echo "[venv_setup] Installing Adafruit_DHT for DHT22 sensor..."
  pip install Adafruit-DHT --config-settings="--build-option=--force-pi" || {
    echo "Warning: Adafruit-DHT installation failed, DHT22 sensor will not work"
  }
  
  echo "[venv_setup] ✓ All packages installed"
else
  echo "No requirements file found at $REQ_FILE; virtualenv created but nothing installed."
fi

echo "Virtualenv ready at $VENV_DIR. To activate: source $VENV_DIR/bin/activate"
