#!/usr/bin/env bash
# Fix for ft5x06 touch device detection timeout issue
# 
# Problem: edt_ft5x06 driver probe failing with error -110 (timeout)
# Cause: IRQ-driven probe was hanging on interrupt line initialization
# Solution: Add edt-ft5406 overlay with polling_mode parameter
#
# Apply this fix to /boot/firmware/config.txt

set -euo pipefail

echo "=== ft5x06 Touch Device Fix ==="
echo ""
echo "Backing up /boot/firmware/config.txt..."
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%s)

echo "Adding edt-ft5406 overlay with polling_mode..."
sudo sed -i '/^dtoverlay=vc4-kms-dsi-7inch$/a dtoverlay=edt-ft5406,polling_mode' /boot/firmware/config.txt

echo ""
echo "Updated overlays:"
grep '^dtoverlay=vc4-kms-dsi\|^dtoverlay=edt-ft5406' /boot/firmware/config.txt
echo ""

echo "Rebooting to apply the fix..."
echo "The touch device should be detected after reboot."
echo ""
sudo reboot
