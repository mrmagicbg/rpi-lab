#!/usr/bin/env bash
# venv_setup.sh - Create Python virtualenv with prerequisite checking
#
# This script checks for system dependencies, installs missing ones,
# creates a Python virtualenv, and installs all required Python packages.
#
# Features:
# - Comprehensive prerequisite checking with status output
# - Automatic installation of missing system packages
# - Clear before/after status for all dependencies
# - Python package installation with error handling
# - Supports both system and venv-based operations
#
# Usage: sudo bash install/venv_setup.sh
# Environment Variables:
#   VENV_DIR  - Virtual environment path (default: /opt/rpi-lab/.venv)
#   APP_DIR   - Application directory (default: /opt/rpi-lab)

set -euo pipefail

# Configuration
VENV_DIR="${VENV_DIR:-/opt/rpi-lab/.venv}"
APP_DIR="${APP_DIR:-/opt/rpi-lab}"
REQ_FILE="$APP_DIR/requirements.txt"

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

# Root check
if [ "$EUID" -ne 0 ]; then
  warn "Running as non-root. Some system packages may not install."
  warn "For full functionality, run with: sudo bash $0"
fi

echo ""
echo "=========================================================================="
echo "  RPI Lab Virtual Environment Setup"
echo "=========================================================================="
echo ""

# Prerequisites list
declare -A SYSTEM_PACKAGES=(
  ["python3"]="Python 3 runtime"
  ["python3-dev"]="Python 3 development files"
  ["python3-full"]="Python 3 full distribution"
  ["build-essential"]="C/C++ build toolchain"
  ["python3-smbus"]="I2C system library"
  ["i2c-tools"]="I2C utilities"
  ["git"]="Version control"
  ["curl"]="HTTP client (for debugging)"
  ["libatlas-base-dev"]="BLAS/LAPACK (for numerical libs)"
)

declare -A PYTHON_PACKAGES=(
  ["bme680"]="2.0.0"
  ["smbus2"]="0.6.0"
  ["evdev"]="1.9.2"
  ["rich"]="13.3.0"
  ["loguru"]="0.7.0"
  ["RPi.GPIO"]="0.7.1"
  ["paho-mqtt"]="1.6.1"
)

# Function to check if system package is installed
is_system_package_installed() {
  dpkg -l | grep -q "^ii  $1 " && return 0 || return 1
}

# Function to check if Python package is installed
is_python_package_installed() {
  "$VENV_DIR/bin/python" -c "import $1" 2>/dev/null && return 0 || return 1
}

# Phase 1: Check and install system prerequisites
echo "PHASE 1: System Dependencies"
echo "=========================================================================="
echo ""

missing_system_packages=()
installed_system_packages=()

for pkg in "${!SYSTEM_PACKAGES[@]}"; do
  if is_system_package_installed "$pkg"; then
    ok "INSTALLED: $pkg (${SYSTEM_PACKAGES[$pkg]})"
    installed_system_packages+=("$pkg")
  else
    warn "MISSING:   $pkg (${SYSTEM_PACKAGES[$pkg]})"
    missing_system_packages+=("$pkg")
  fi
done

echo ""
echo "Summary:"
echo "  Installed: ${#installed_system_packages[@]}/${#SYSTEM_PACKAGES[@]}"
echo "  Missing:   ${#missing_system_packages[@]}/${#SYSTEM_PACKAGES[@]}"
echo ""

if [ ${#missing_system_packages[@]} -gt 0 ]; then
  echo "Installing missing system packages..."
  apt-get update -y || warn "apt-get update failed; continuing anyway"
  
  for pkg in "${missing_system_packages[@]}"; do
    log "Installing $pkg..."
    apt-get install -y "$pkg" || warn "Failed to install $pkg; continuing"
  done
  
  echo ""
  ok "System package installation complete"
fi

echo ""

# Phase 2: Create virtual environment
echo "PHASE 2: Python Virtual Environment"
echo "=========================================================================="
echo ""

if [ -d "$VENV_DIR" ]; then
  warn "Virtual environment already exists at $VENV_DIR"
  read -p "Recreate it? [y/N]: " -r
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Removing existing venv..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR" || { err "Failed to create venv"; exit 1; }
    ok "Created new venv at $VENV_DIR"
  fi
else
  log "Creating new Python virtual environment..."
  python3 -m venv "$VENV_DIR" || { err "Failed to create venv"; exit 1; }
  ok "Created venv at $VENV_DIR"
fi

echo ""

# Phase 3: Install Python packages
echo "PHASE 3: Python Packages (from requirements.txt)"
echo "=========================================================================="
echo ""

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

log "Upgrading pip, setuptools, and wheel..."
"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel -q || warn "pip upgrade had issues"

echo ""

if [ -f "$REQ_FILE" ]; then
  log "Installing packages from $REQ_FILE..."
  
  # Check current state before install
  echo ""
  echo "Before installation:"
  for pkg in "${!PYTHON_PACKAGES[@]}"; do
    if is_python_package_installed "$pkg"; then
      ok "INSTALLED: $pkg"
    else
      warn "MISSING:   $pkg (required version: ${PYTHON_PACKAGES[$pkg]})"
    fi
  done
  
  echo ""
  log "Running pip install -r requirements.txt..."
  "$VENV_DIR/bin/pip" install -r "$REQ_FILE" || { err "pip install failed"; exit 1; }
  
  echo ""
  echo "After installation:"
  all_installed=1
  for pkg in "${!PYTHON_PACKAGES[@]}"; do
    if is_python_package_installed "$pkg"; then
      ok "INSTALLED: $pkg"
    else
      err "FAILED:    $pkg (${PYTHON_PACKAGES[$pkg]})"
      all_installed=0
    fi
  done
  
  if [ $all_installed -eq 1 ]; then
    echo ""
    ok "All Python packages installed successfully"
  else
    echo ""
    warn "Some Python packages failed to install; check output above"
  fi
else
  err "No requirements file found at $REQ_FILE"
  err "Cannot proceed with Python package installation"
  exit 1
fi

echo ""

# Final summary
echo "=========================================================================="
echo "  SETUP COMPLETE"
echo "=========================================================================="
echo ""
ok "Virtual environment ready at: $VENV_DIR"
ok "To activate: source $VENV_DIR/bin/activate"
ok ""
ok "Next steps:"
ok "  1. Activate venv: source $VENV_DIR/bin/activate"
ok "  2. Run GUI installer: sudo bash $APP_DIR/install/install_gui.sh"
ok "  3. Wire BME690 sensor (I2C 0x76 or 0x77)"
ok "  4. Verify: i2cdetect -y 1"
ok ""
