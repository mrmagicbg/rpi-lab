#!/usr/bin/env bash
# Script to setup Waveshare 4.3inch DSI LCD on Raspberry Pi 3
# Reference: https://www.waveshare.com/wiki/4.3inch_DSI_LCD

set -euo pipefail

CONFIG="/boot/config.txt"
OVERLAY_LINE="dtoverlay=vc4-kms-dsi-4.3inch"

echo "Starting Waveshare 4.3inch DSI setup..."

if [ ! -f "$CONFIG" ]; then
    echo "ERROR: $CONFIG not found. Are you running on a Raspberry Pi?" >&2
    exit 2
fi

# Backup config.txt (idempotent)
if ! grep -Fxq "$OVERLAY_LINE" "$CONFIG"; then
    sudo cp -v "$CONFIG" "${CONFIG}.bak.$(date +%s)"
    echo "Adding display overlay to $CONFIG"
    echo "" | sudo tee -a "$CONFIG" >/dev/null
    echo "$OVERLAY_LINE" | sudo tee -a "$CONFIG" >/dev/null
else
    echo "Overlay already present in $CONFIG"
fi

echo "Updating packages and installing touch/input utilities (idempotent)"
sudo apt-get update
sudo apt-get install -y --no-install-recommends xserver-xorg-input-evdev xinput-calibrator tslib

echo "If you need touch calibration, run: sudo xinput_calibrator (when X is running)"

cat <<'EOF'
Setup complete.

Notes:
- A reboot is required for the overlay changes to take effect.
- If you plan to run the TUI on the console (no X), ensure the service runs on a TTY.
EOF

read -p "Reboot now? (y/N): " REBOOT
case "${REBOOT,,}" in
  y|yes)
    echo "Rebooting..."
    sudo reboot
    ;;
  *)
    echo "Please reboot manually to apply changes."
    ;;
esac
#!/bin/bash
# Script to setup Waveshare 4.3inch DSI LCD on Raspberry Pi 3
# Reference: https://www.waveshare.com/wiki/4.3inch_DSI_LCD

set -e

# Update system
sudo apt update && sudo apt upgrade -y

# Enable DSI display overlay
sudo sed -i '/^#dtoverlay=vc4-kms-dsi-7inch$/a dtoverlay=vc4-kms-dsi-4.3inch' /boot/config.txt

# Enable touch support (should be automatic, but ensure evdev is installed)
sudo apt install -y xserver-xorg-input-evdev

# Reboot required for changes to take effect
read -p "Setup complete. Reboot now? (y/n): " REBOOT
if [[ "$REBOOT" =~ ^[Yy]$ ]]; then
    sudo reboot
else
    echo "Please reboot manually to apply changes."
fi
