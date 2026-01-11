#!/usr/bin/env bash
# install_gui.sh - Install RPI Lab GUI with prerequisite checking
#
# This script configures the system for RPI Lab GUI operation:
# - Checks for system prerequisites (GPIO tools, I2C, display)
# - Configures GPIO permissions for the mrpi user
# - Creates systemd service for autostart
# - Verifies I2C connectivity to BME690 sensor
#
# Usage: sudo bash install/install_gui.sh
# Environment Variables:
#   APP_DIR  - Application directory (default: /opt/rpi-lab)
#   APP_USER - Application user (default: mrpi)

set -euo pipefail

# Configuration
APP_DIR="${APP_DIR:-/opt/rpi-lab}"
APP_USER="${APP_USER:-mrpi}"
VENV_DIR="$APP_DIR/.venv"
SERVICE_FILE="/etc/systemd/system/rpi_gui.service"

# Colors for output
COLOR_RED='\033[0;31m'
COLOR_GRN='\033[0;32m'
COLOR_YLW='\033[0;33m'
COLOR_BLU='\033[0;34m'
COLOR_RST='\033[0m'

log() { echo -e "${COLOR_BLU}➤${COLOR_RST} $*"; }
ok() { echo -e "${COLOR_GRN}✓${COLOR_RST} $*"; }
warn() { echo -e "${COLOR_YLW}⚠${COLOR_RST} $*"; }
err() { echo -e "${COLOR_RED}✗${COLOR_RST} $*"; }
die() { err "$*"; exit 1; }

# Require root
[ "$EUID" -eq 0 ] || die "Must run as root (sudo)"

echo ""
echo "=========================================================================="
echo "  RPI Lab GUI Installation"
echo "=========================================================================="
echo ""

# Phase 1: Prerequisite checking
echo "PHASE 1: System Prerequisites"
echo "=========================================================================="
echo ""

# Check Python venv
if [ ! -d "$VENV_DIR" ]; then
  warn "Virtual environment not found at $VENV_DIR"
  err "Run: sudo bash $APP_DIR/install/venv_setup.sh first"
  exit 1
fi
ok "Virtual environment exists"

# Check required system packages
declare -a REQUIRED_PACKAGES=("python3" "xserver-xorg" "fbset" "git" "i2c-tools")
missing_pkgs=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
  if dpkg -l | grep -q "^ii  $pkg "; then
    ok "System package installed: $pkg"
  else
    warn "System package missing: $pkg"
    missing_pkgs+=("$pkg")
  fi
done

if [ ${#missing_pkgs[@]} -gt 0 ]; then
  log "Installing missing system packages..."
  apt-get update -y || warn "apt-get update had issues"
  for pkg in "${missing_pkgs[@]}"; do
    log "Installing $pkg..."
    apt-get install -y "$pkg" || warn "Failed to install $pkg"
  done
  echo ""
fi

# Check I2C enabled
echo ""
log "Checking I2C configuration..."
if grep -q "^dtparam=i2c_arm=on" /boot/firmware/config.txt 2>/dev/null || \
   grep -q "^dtparam=i2c1=on" /boot/firmware/config.txt 2>/dev/null || \
   grep -q "^dtparam=i2c_arm=on" /boot/config.txt 2>/dev/null; then
  ok "I2C enabled in firmware config"
else
  warn "I2C may not be enabled"
  warn "Enable with: sudo raspi-config nonint do_i2c 0"
  warn "Or add to /boot/firmware/config.txt: dtparam=i2c_arm=on,i2c_arm_baudrate=400000"
fi

# Check I2C tools
if command -v i2cdetect >/dev/null 2>&1; then
  ok "i2cdetect available"
else
  warn "i2cdetect not found; installing i2c-tools"
  apt-get install -y i2c-tools || warn "Failed to install i2c-tools"
fi

# Try to detect BME690 sensor
echo ""
log "Attempting to detect BME690 sensor on I2C bus 1..."
if command -v i2cdetect >/dev/null 2>&1; then
  if i2cdetect -y 1 2>/dev/null | grep -E "76|77" >/dev/null; then
    ok "BME690 sensor detected (address 0x76 or 0x77)"
  else
    warn "BME690 sensor NOT detected on I2C bus 1"
    warn "Check wiring: VIN → 3.3V, GND → GND, SDA → GPIO2, SCL → GPIO3"
    warn "Verify with: i2cdetect -y 1"
  fi
else
  warn "Cannot check I2C; i2cdetect not installed"
fi

echo ""

# Phase 2: User and permissions
echo "PHASE 2: User & Permissions"
echo "=========================================================================="
echo ""

# Create user if needed
if id -u "$APP_USER" >/dev/null 2>&1; then
  ok "User $APP_USER already exists"
else
  log "Creating user $APP_USER..."
  useradd -m -s /bin/bash "$APP_USER" || warn "Failed to create user"
  ok "User $APP_USER created"
fi

# Add to GPIO group
if getent group gpio >/dev/null; then
  if id -nG "$APP_USER" | grep -qw gpio; then
    ok "User $APP_USER already in gpio group"
  else
    log "Adding $APP_USER to gpio group..."
    usermod -aG gpio "$APP_USER"
    ok "User added to gpio group"
  fi
else
  warn "gpio group does not exist; GPIO access may be limited"
fi

# Add to i2c group
if getent group i2c >/dev/null; then
  if id -nG "$APP_USER" | grep -qw i2c; then
    ok "User $APP_USER already in i2c group"
  else
    log "Adding $APP_USER to i2c group..."
    usermod -aG i2c "$APP_USER"
    ok "User added to i2c group"
  fi
else
  warn "i2c group does not exist"
fi

# Fix directory permissions
log "Setting directory permissions..."
chown -R "$APP_USER:$APP_USER" "$APP_DIR" || warn "Failed to set permissions"
chmod 755 "$APP_DIR" || warn "Failed to set dir permissions"
ok "Directory permissions set"

echo ""

# Phase 3: Systemd service
echo "PHASE 3: Systemd Service"
echo "=========================================================================="
echo ""

log "Creating systemd service file: $SERVICE_FILE"

cat > "$SERVICE_FILE" <<'SERVICEEOF'
[Unit]
Description=RPI Lab GUI Control Panel
After=network.target X11.target
PartOf=graphical.target

[Service]
Type=simple
User=mrpi
WorkingDirectory=/opt/rpi-lab
ExecStart=/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_gui.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/mrpi/.Xauthority"
Environment="BME690_DRY_RUN=0"
TimeoutStopSec=5

[Install]
WantedBy=graphical.target
SERVICEEOF

ok "Service file created"

# Reload systemd
log "Reloading systemd daemon..."
systemctl daemon-reload || warn "Failed to reload systemd"

# Enable service
log "Enabling service for autostart..."
systemctl enable rpi_gui.service || warn "Failed to enable service"
ok "Service enabled"

echo ""

# Phase 4: Verification
echo "PHASE 4: Verification"
echo "=========================================================================="
echo ""

log "Service status:"
systemctl status rpi_gui.service --no-pager 2>/dev/null || warn "Service status check failed"

echo ""
log "Testing venv and imports..."
if "$VENV_DIR/bin/python" -c "import bme680; print('✓ bme680 library available')" 2>/dev/null; then
  ok "bme680 library available"
else
  warn "bme680 library not found"
fi

if "$VENV_DIR/bin/python" -c "import tkinter; print('✓ tkinter available')" 2>/dev/null; then
  ok "tkinter library available"
else
  warn "tkinter not found; install with: sudo apt install python3-tk"
fi

echo ""

# Final summary
echo "=========================================================================="
echo "  INSTALLATION COMPLETE"
echo "=========================================================================="
echo ""
ok "RPI Lab GUI installed successfully"
ok ""
ok "Next steps:"
ok "  1. Verify I2C: sudo i2cdetect -y 1 (should show 76 or 77)"
ok "  2. Test GUI: /opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_gui.py"
ok "  3. View logs: journalctl -u rpi_gui.service -f"
ok "  4. Start on boot: systemctl is-enabled rpi_gui.service"
ok ""
ok "Service commands:"
ok "  sudo systemctl start rpi_gui.service"
ok "  sudo systemctl stop rpi_gui.service"
ok "  sudo systemctl restart rpi_gui.service"
ok "  sudo systemctl status rpi_gui.service"
ok ""

mrmagic ALL=(ALL) NOPASSWD: /opt/rpi-lab/.venv/bin/python
SUDOERS
    chmod 440 "$SUDOERS_FILE"
    echo "[install_gui] ✓ Sudoers configured at $SUDOERS_FILE"
else
    echo "[install_gui] Sudoers file already exists: $SUDOERS_FILE"
fi

# Add mrmagic user to i2c group for BME690 access
echo "[install_gui] Adding mrmagic user to i2c group..."
if ! id -nG mrmagic | grep -qw i2c; then
    usermod -a -G i2c mrmagic
    echo "[install_gui] ✓ Added mrmagic to i2c group"
else
    echo "[install_gui] User already in i2c group"
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
