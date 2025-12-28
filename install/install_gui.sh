#!/usr/bin/env bash
# Install GUI mode dependencies and configure auto-start
#
# Installs:
#   - X11 server (lightweight for embedded)
#   - Window manager (openbox or similar)
#   - python3-tk for tkinter GUI
#   - xterm for terminal access from GUI
#   - Configures auto-login and X11 auto-start
#
# Usage: sudo bash install/install_gui.sh

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo $0"
  exit 1
fi

echo "[install_gui] Installing GUI dependencies..."

# Update package list
apt-get update -y

# Install X11 server and minimal window manager
echo "[install_gui] Installing X11 server and window manager..."
apt-get install -y \
  xserver-xorg \
  xserver-xorg-video-fbdev \
  xinit \
  x11-xserver-utils \
  openbox \
  python3-tk \
  xterm \
  lightdm

# Install the GUI service
echo "[install_gui] Installing rpi_gui systemd service..."
cp /opt/rpi-lab/gui/rpi_gui.service /etc/systemd/system/rpi_gui.service
chmod 644 /etc/systemd/system/rpi_gui.service

# Configure sudoers for passwordless reboot and GPIO access
SUDOERS_FILE="/etc/sudoers.d/rpi-lab"
if [ ! -f "$SUDOERS_FILE" ]; then
    echo "[install_gui] Configuring sudoers for passwordless reboot..."
    cat > "$SUDOERS_FILE" << 'SUDOERS'
# RPI Lab - Allow mrmagic user to reboot without password
mrmagic ALL=(ALL) NOPASSWD: /sbin/reboot

# Allow GPIO access via python without password
mrmagic ALL=(ALL) NOPASSWD: /opt/rpi-lab/.venv/bin/python
SUDOERS
    chmod 440 "$SUDOERS_FILE"
    echo "[install_gui] ✓ Sudoers configured at $SUDOERS_FILE"
else
    echo "[install_gui] Sudoers file already exists: $SUDOERS_FILE"
fi

# Add mrmagic user to gpio group for hardware access
echo "[install_gui] Adding mrmagic user to gpio group..."
if ! id -nG mrmagic | grep -qw gpio; then
    usermod -a -G gpio mrmagic
    echo "[install_gui] ✓ Added mrmagic to gpio group"
else
    echo "[install_gui] User already in gpio group"
fi

# Enable auto-login for mrmagic user
echo "[install_gui] Configuring LightDM auto-login..."
LIGHTDM_CONF="/etc/lightdm/lightdm.conf"
if [ -f "$LIGHTDM_CONF" ]; then
    # Backup original
    cp "$LIGHTDM_CONF" "$LIGHTDM_CONF.backup.$(date +%Y%m%dT%H%M%S)"
    
    # Enable auto-login
    if ! grep -q "^autologin-user=" "$LIGHTDM_CONF"; then
        sed -i '/^\[Seat:\*\]/a autologin-user=mrmagic' "$LIGHTDM_CONF"
    else
        sed -i 's/^autologin-user=.*/autologin-user=mrmagic/' "$LIGHTDM_CONF"
    fi
    
    if ! grep -q "^autologin-user-timeout=" "$LIGHTDM_CONF"; then
        sed -i '/^\[Seat:\*\]/a autologin-user-timeout=0' "$LIGHTDM_CONF"
    else
        sed -i 's/^autologin-user-timeout=.*/autologin-user-timeout=0/' "$LIGHTDM_CONF"
    fi
else
    echo "[install_gui] WARNING: LightDM config not found at $LIGHTDM_CONF"
fi

# Create .xsession for openbox auto-start
XSESSION_FILE="/home/mrmagic/.xsession"
if [ ! -f "$XSESSION_FILE" ]; then
    echo "[install_gui] Creating .xsession for openbox..."
    cat > "$XSESSION_FILE" << 'XSESSION'
#!/bin/bash
# Start openbox window manager
exec openbox-session
XSESSION
    chown mrmagic:mrmagic "$XSESSION_FILE"
    chmod +x "$XSESSION_FILE"
fi

# Reload systemd and enable GUI service
echo "[install_gui] Enabling rpi_gui service..."
systemctl daemon-reload
systemctl enable rpi_gui.service

cat << 'EOF'

[install_gui] GUI installation complete!

Summary:
  - X11 server and openbox window manager installed
  - python3-tk for tkinter GUI installed
  - rpi_gui.service enabled (auto-starts on boot)
  - Auto-login configured for user 'mrmagic'
  - Sudoers configured for passwordless reboot

Next steps:
  1. Reboot to start the GUI:
       sudo reboot
  
  2. After reboot, the GUI should appear on the display
  
  3. To manually start the GUI service:
       sudo systemctl start rpi_gui.service
  
  4. To check GUI logs:
       journalctl -u rpi_gui.service -f

EOF
