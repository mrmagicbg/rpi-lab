#!/bin/sh
# Wrapper to delay start then exec the TUI under the service's TTY
cd /opt/rpi-lab/tui || exit 1
sleep 10
exec /opt/rpi-lab/.venv/bin/python /opt/rpi-lab/tui/rpi_tui.py
