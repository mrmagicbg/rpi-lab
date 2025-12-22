#!/usr/bin/env bash
# Quick touch test for 4.3" DSI LCD
# Shows touch events live for 15 seconds

set -euo pipefail

echo "=== Touch Test for 4.3inch DSI LCD ==="
echo ""
echo "Touch devices found:"
cat /proc/bus/input/devices | grep -A 8 "ft5x06\|goodix\|raspberrypi-ts" || echo "No touch devices detected!"
echo ""
echo "Running evtest on primary touch device for 15 seconds..."
echo "Touch the screen now!"
echo ""

# Find the first touch device (ft5x06 or raspberrypi-ts)
TOUCH_DEV=$(cat /proc/bus/input/devices | grep -B 5 "ft5x06\|goodix\|raspberrypi-ts" | grep "Handlers.*event" | head -n 1 | sed 's/.*event\([0-9]\+\).*/\1/')

if [ -z "$TOUCH_DEV" ]; then
    echo "ERROR: No touch device found!"
    exit 1
fi

echo "Using /dev/input/event$TOUCH_DEV"
echo ""
sudo timeout 15 evtest /dev/input/event$TOUCH_DEV || echo "Done!"
