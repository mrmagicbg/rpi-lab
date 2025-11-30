#!/usr/bin/env bash
# Wrapper to run display installer non-interactively (useful for automated installs)
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

# Run installer with --no-reboot so the main installer controls reboot
bash "$DISPLAY_SCRIPT" --no-reboot

echo "Installing Python touch support (evdev)..."
sudo apt-get update
sudo apt-get install -y python3-pip
sudo pip3 install evdev
echo "Display installation finished (no reboot)."
