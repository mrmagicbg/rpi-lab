#!/usr/bin/env bash
# Non-interactive installer for Waveshare 4.3" DSI LCD Rev 2.2 + touch
#
# Idempotently:
#   - Configures /boot*/config.txt for the working overlay combination
#     dtoverlay=vc4-kms-dsi-waveshare-800x480
#     dtoverlay=edt-ft5406,polling_mode
#   - Disables display_auto_detect (we manage the DSI panel explicitly)
#   - Installs helper tools (evtest, i2c-tools) for debugging
#
# Python touch support (evdev) is installed into the project venv via
#   install/venv_setup.sh using tui/requirements.txt.

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo $0"
  exit 1
fi

DISPLAY_SCRIPT="/opt/rpi-lab/display/setup_waveshare_4.3inch_dsi.sh"

if [ ! -f "$DISPLAY_SCRIPT" ]; then
  echo "Display script not found at $DISPLAY_SCRIPT"
  exit 2
fi

echo "[display_install] Applying Waveshare 4.3\" DSI Rev 2.2 config..."
# Run installer with --no-reboot so the caller controls reboot timing
bash "$DISPLAY_SCRIPT" --no-reboot

echo "[display_install] Installing debugging tools (evtest, i2c-tools)..."
apt-get update -y
apt-get install -y evtest i2c-tools

echo "[display_install] Done. Reboot is still required for overlay changes to take effect."
