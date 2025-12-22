#!/usr/bin/env bash
# Fix for ft5x06 touch device detection timeout issue
#
# Problem: edt_ft5x06 driver probe failing with error -110 (timeout)
# Cause: IRQ-driven probe was hanging on interrupt line initialization
# Solution: Ensure the edt-ft5406 overlay is present with polling_mode
#
# This script normalizes the touch overlay in the active config.txt without
# changing the display overlay (vc4-kms-dsi-waveshare-800x480).

set -euo pipefail

FALLBACK_CONFIG="/boot/config.txt"
FIRMWARE_CONFIG="/boot/firmware/config.txt"
CONFIG="$FALLBACK_CONFIG"
if [ -f "$FIRMWARE_CONFIG" ]; then
	CONFIG="$FIRMWARE_CONFIG"
fi

echo "=== ft5x06 Touch Device Fix ==="
echo "Using config file: $CONFIG"
echo ""

if [ ! -f "$CONFIG" ]; then
	echo "ERROR: $CONFIG not found. Are you running on a Raspberry Pi?" >&2
	exit 2
fi

echo "Backing up $CONFIG..."
cp "$CONFIG" "$CONFIG.backup.$(date +%Y%m%dT%H%M%S)"

TOUCH_LINE='dtoverlay=edt-ft5406,polling_mode'

if grep -q '^dtoverlay=edt-ft5406' "$CONFIG"; then
	# Normalize existing edt-ft5406 entry
	sed -i 's/^dtoverlay=edt-ft5406.*/dtoverlay=edt-ft5406,polling_mode/' "$CONFIG"
elif ! grep -q "^$TOUCH_LINE" "$CONFIG"; then
	echo "$TOUCH_LINE" >> "$CONFIG"
fi

echo ""
echo "Updated overlays (display + touch):"
grep '^dtoverlay=vc4-kms-dsi\|^dtoverlay=edt-ft5406' "$CONFIG" || true
echo ""

echo "Rebooting to apply the fix..."
echo "The ft5x06 touch device should be detected after reboot."
echo ""
reboot
