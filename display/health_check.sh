#!/usr/bin/env bash
# Health check for 4.3" DSI LCD display and touch setup

set -euo pipefail

echo "=============================================="
echo "  4.3inch DSI LCD Rev 2.2 - Health Check"
echo "=============================================="
echo ""

# 1. Overlay configuration
echo "1. Display Overlay Configuration:"
echo "   Current overlay in /boot/firmware/config.txt:"
grep -E "^dtoverlay=vc4-kms-dsi" /boot/firmware/config.txt || echo "   ❌ No DSI overlay found!"
echo ""

# 2. Framebuffer devices
echo "2. Framebuffer Devices:"
if [ -e /dev/fb0 ]; then
    echo "   ✓ /dev/fb0 exists"
else
    echo "   ❌ /dev/fb0 missing!"
fi
echo ""

# 3. Backlight
echo "3. Backlight Status:"
for bl in /sys/class/backlight/*; do
    if [ -d "$bl" ]; then
        name=$(basename "$bl")
        bright=$(cat "$bl/brightness" 2>/dev/null || echo "N/A")
        max=$(cat "$bl/max_brightness" 2>/dev/null || echo "N/A")
        echo "   $name: $bright / $max"
    fi
done
echo ""

# 4. Touch devices
echo "4. Touch Input Devices:"
cat /proc/bus/input/devices | grep -B 1 -A 7 "ft5x06\|goodix\|raspberrypi-ts" | grep -E "Name=|Handlers=" || echo "   ❌ No touch devices found!"
echo ""

# 5. TUI service
echo "5. RPI TUI Service:"
systemctl is-active rpi_tui.service >/dev/null 2>&1 && echo "   ✓ rpi_tui.service is active" || echo "   ❌ rpi_tui.service is not active"
ps aux | grep -v grep | grep rpi_tui.py >/dev/null 2>&1 && echo "   ✓ TUI process is running" || echo "   ⚠  TUI process not found"
echo ""

# 6. Console blanking
echo "6. Console Blanking:"
grep -o "consoleblank=0" /boot/firmware/cmdline.txt >/dev/null 2>&1 && echo "   ✓ Console blanking disabled (consoleblank=0)" || echo "   ⚠  Console may blank after idle"
echo ""

echo "=============================================="
echo "  Health Check Complete"
echo "=============================================="
echo ""
echo "To test touch interactively, run:"
echo "  sudo /opt/rpi-lab/display/test_touch.sh"
echo ""
