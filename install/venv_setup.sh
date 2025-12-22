#!/usr/bin/env bash
# Create a Python virtualenv for the RPI Lab and install requirements
set -euo pipefail

VENV_DIR="/opt/rpi-lab/.venv"
REQ_FILE="/opt/rpi-lab/requirements.txt"

if [ "$EUID" -ne 0 ]; then
  echo "Warning: running as non-root. The venv will be created in $PWD unless you run with sudo."
fi

python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if [ -f "$REQ_FILE" ]; then
  pip install --upgrade pip
  pip install -r "$REQ_FILE"
else
  echo "No requirements file found at $REQ_FILE; virtualenv created but nothing installed."
fi

echo "Virtualenv ready at $VENV_DIR. To activate: source $VENV_DIR/bin/activate"
