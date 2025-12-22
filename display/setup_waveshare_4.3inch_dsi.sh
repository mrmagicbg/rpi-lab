#!/usr/bin/env bash
# Waveshare 4.3" DSI LCD Rev 2.2 + ft5x06 touch
#
# This installer applies the *known working* overlay configuration used
# in production:
#   - dtoverlay=vc4-kms-dsi-waveshare-800x480
#   - dtoverlay=edt-ft5406,polling_mode
#   - display_auto_detect=0
#   - max_framebuffers=2
#
# It is idempotent and only touches the relevant lines in config.txt.
#
# Usage: sudo ./setup_waveshare_4.3inch_dsi.sh [--reboot] [--no-reboot]

set -euo pipefail

FALLBACK_CONFIG="/boot/config.txt"
FIRMWARE_CONFIG="/boot/firmware/config.txt"
CONFIG="$FALLBACK_CONFIG"
if [ -f "$FIRMWARE_CONFIG" ]; then
  CONFIG="$FIRMWARE_CONFIG"
fi

DO_REBOOT="prompt"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --reboot) DO_REBOOT=yes; shift ;;
    --no-reboot) DO_REBOOT=no; shift ;;
    -h|--help) echo "Usage: $0 [--reboot|--no-reboot]"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done

echo "[waveshare-4.3] Starting Waveshare 4.3inch DSI Rev 2.2 setup..."

if [ ! -f "$CONFIG" ]; then
    echo "ERROR: $CONFIG not found. Are you running on a Raspberry Pi?" >&2
    exit 2
fi

# Backup config if not already backed up
if [ ! -f "${CONFIG}.orig" ]; then
  cp -v "$CONFIG" "${CONFIG}.orig"
fi

TS_SUFFIX="$(date +%Y%m%dT%H%M%S)"
cp -v "$CONFIG" "${CONFIG}.bak.waveshare.$TS_SUFFIX"

echo "[waveshare-4.3] Using config file: $CONFIG"

# 1) Disable automatic display detection so our DSI overlay is authoritative
if grep -q '^display_auto_detect=' "$CONFIG"; then
  sed -i 's/^display_auto_detect=.*/display_auto_detect=0/' "$CONFIG"
else
  printf '\n# Manually configure DSI display (disable auto-detect)\n' | tee -a "$CONFIG" >/dev/null
  echo "display_auto_detect=0" | tee -a "$CONFIG" >/dev/null
fi

# 2) Ensure the Waveshare DSI overlay is present and no conflicting vc4-kms-dsi-* overlays
WAVESHARE_LINE='dtoverlay=vc4-kms-dsi-waveshare-800x480'

# Comment any other vc4-kms-dsi-* overlays that might conflict
sed -i \
  -e '/^dtoverlay=vc4-kms-dsi-waveshare-800x480/!{/^dtoverlay=vc4-kms-dsi-/s/^/# /}' \
  "$CONFIG"

if ! grep -q "^$WAVESHARE_LINE" "$CONFIG"; then
  printf '\n# Waveshare 4.3" DSI LCD Rev 2.2 (800x480)\n' | tee -a "$CONFIG" >/dev/null
  echo "$WAVESHARE_LINE" | tee -a "$CONFIG" >/dev/null
fi

# 3) Ensure ft5x06 touch overlay with polling_mode is present
TOUCH_LINE='dtoverlay=edt-ft5406,polling_mode'

if grep -q '^dtoverlay=edt-ft5406' "$CONFIG"; then
  # Normalize to polling_mode variant
  sed -i 's/^dtoverlay=edt-ft5406.*/dtoverlay=edt-ft5406,polling_mode/' "$CONFIG"
elif ! grep -q "^$TOUCH_LINE" "$CONFIG"; then
  echo "$TOUCH_LINE" | tee -a "$CONFIG" >/dev/null
fi

# 4) Ensure max_framebuffers=2 (helps with multiple framebuffers on KMS)
if ! grep -q '^max_framebuffers=' "$CONFIG"; then
  echo "max_framebuffers=2" | tee -a "$CONFIG" >/dev/null
fi

cat <<'EOF2'
[waveshare-4.3] Setup complete.

Notes:
- A reboot is required for the overlay changes to take effect.
- Use /opt/rpi-lab/display/health_check.sh to verify display + touch.
- Use /opt/rpi-lab/display/test_touch.sh to see live touch events.
EOF2

case "$DO_REBOOT" in
  yes)
    echo "[waveshare-4.3] Rebooting..."
    reboot
    ;;
  no)
    echo "[waveshare-4.3] Skipping reboot as requested. Please reboot manually."
    ;;
  prompt)
    read -p "Reboot now? (y/N): " REBOOT
    case "${REBOOT,,}" in
      y|yes) reboot ;;
      *) echo "[waveshare-4.3] Please reboot manually to apply changes." ;;
    esac
    ;;
esac
