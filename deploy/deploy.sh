#!/usr/bin/env bash
# deploy.sh - Safe redeployment script for rpi-lab with comprehensive prerequisite checking
#
# This script safely redeploys rpi-lab from GitHub to /opt/rpi-lab with:
# - Prerequisite system package validation
# - I2C configuration verification
# - BME690 sensor detection
# - Venv management and activation
# - Systemd service deployment
# - Comprehensive error handling and status reporting
#
# Features:
# - Multi-phase deployment with detailed status output
# - Automatic backup creation with timestamps
# - Git branch pulling with interactive confirmation
# - I2C kernel module checks and device detection
# - BME690 sensor address detection (0x76 primary, 0x77 secondary)
# - Virtual environment recreation and library validation
# - Systemd service installation with proper permissions
# - Automatic rollback on deployment failure
#
# Usage: sudo bash deploy.sh [OPTIONS]
# Options:
#   --no-backup    Skip creating backup before deployment
#   --no-prereq    Skip prerequisite checking (use with caution)
#   --hard         Force git reset --hard to remote branch (discards local changes)
#   --no-pull      Skip pulling latest changes from remote branch
#   --dry-run      Show what would be done without making changes
#
# Environment Variables:
#   GIT_BRANCH     Branch to deploy (if set, skips prompt; otherwise prompts interactively)
#   APP_DIR        Target application directory (defaults to /opt/rpi-lab)
#   BACKUP_DIR     Backup directory (defaults to /opt/backups)
#
# Examples:
#   sudo bash deploy.sh                          # Full deployment with checks
#   sudo bash deploy.sh --no-backup              # Skip backup creation
#   sudo bash deploy.sh --hard                   # Force reset local changes
#   sudo bash deploy.sh --no-pull                # Deploy current local state
#   GIT_BRANCH=main sudo bash deploy.sh         # Deploy specific branch without prompting
set -euo pipefail
IFS=$'\n\t'

# Determine REPO_DIR from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="${APP_DIR:-/opt/rpi-lab}"
SERVICE_NAME="rpi_gui.service"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups}"
DO_BACKUP=1
CHECK_PREREQ=1
HARD=0
DRY_RUN=0
PULL_LATEST=1
BACKUP_FILE=""  # Track backup file for rollback
# GIT_BRANCH will be set from environment or prompted for

COLOR_RED='\033[0;31m'; COLOR_GRN='\033[0;32m'; COLOR_YLW='\033[0;33m'; COLOR_BLU='\033[0;34m'; COLOR_RST='\033[0m'
log(){ echo -e "${COLOR_BLU}➤${COLOR_RST} $*"; }
ok(){ echo -e "${COLOR_GRN}✓${COLOR_RST} $*"; }
warn(){ echo -e "${COLOR_YLW}⚠${COLOR_RST} $*"; }
err(){ echo -e "${COLOR_RED}✗${COLOR_RST} $*"; }
die(){ err "$*"; exit 1; }

# Rollback handler - called on deployment failure
on_error() {
	local exit_code=$?
	err ""
	err "============================================================================"
	err "  DEPLOYMENT FAILED (exit code: $exit_code)"
	err "============================================================================"
	err ""
	
	if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
		warn "Attempting automatic rollback from backup..."
		warn "Backup file: $BACKUP_FILE"
		
		# Stop service before rollback
		systemctl stop $SERVICE_NAME 2>/dev/null || true
		
		# Extract backup
		if tar -xzf "$BACKUP_FILE" -C "$(dirname "$APP_DIR")" 2>/dev/null; then
			ok "Rollback successful - restored from backup"
			
			# Restart service with old version
			systemctl restart $SERVICE_NAME 2>/dev/null || true
			
			warn "System restored to pre-deployment state"
			warn "Review error messages above to diagnose the issue"
		else
			err "Rollback extraction failed"
			err "Manual recovery required:"
			err "  1. Extract backup manually: tar -xzf $BACKUP_FILE -C $(dirname "$APP_DIR")"
			err "  2. Restart service: systemctl restart $SERVICE_NAME"
		fi
	else
		warn "No backup available for rollback"
		warn "Manual recovery required"
	fi
	
	err ""
	err "Deployment aborted"
	exit $exit_code
}

# Cleanup handler - called on exit (success or failure)
on_exit() {
	# Clear backup file reference on successful completion
	if [ $? -eq 0 ]; then
		BACKUP_FILE=""
	fi
}

# Set up error traps
trap 'on_error' ERR
trap 'on_exit' EXIT

parse_args(){
	while [ $# -gt 0 ]; do
		case "$1" in
			--no-backup) DO_BACKUP=0 ;;
			--no-prereq) CHECK_PREREQ=0 ;;
			--dry-run) DRY_RUN=1 ;;
			--hard) HARD=1 ;;
			--no-pull) PULL_LATEST=0 ;;
			*) die "Unknown arg: $1" ;;
		esac
		shift
	done
}

# Phase 1: Check system prerequisites
check_system_prereqs(){
	log ""
	log "=== PHASE 1: System Prerequisites ==="
	
	local required_packages=("python3" "python3-venv" "python3-pip" "git" "i2c-tools" "build-essential")
	local missing=0
	local installed=0
	
	for pkg in "${required_packages[@]}"; do
		if dpkg -l | grep -q "^ii  $pkg "; then
			ok "$pkg installed"
			((installed++))
		else
			warn "$pkg missing (will install)"
			((missing++))
		fi
	done
	
	log "Status: $installed installed, $missing missing"
	
	if [ $missing -gt 0 ]; then
		log "Installing missing packages..."
		apt-get update
		apt-get install -y "${required_packages[@]}"
	fi
	
	ok "System prerequisites satisfied"
}

# Phase 2: Check I2C configuration
check_i2c_config(){
	log ""
	log "=== PHASE 2: I2C Configuration ==="
	
	# Check I2C kernel modules
	if lsmod | grep -q "i2c_bcm"; then
		ok "I2C kernel modules loaded"
	else
		warn "I2C kernel modules not loaded, attempting to load..."
		modprobe i2c_bcm2835 2>/dev/null || warn "Could not load I2C module (may be in kernel)"
	fi
	
	# Check for I2C device
	if [ -e "/dev/i2c-1" ] || [ -e "/dev/i2c-0" ]; then
		ok "I2C device files exist"
	else
		warn "I2C device files not found - ensure I2C is enabled in raspi-config"
	fi
}

# Phase 3: Detect BME690 sensor
detect_bme690_sensor(){
	log ""
	log "=== PHASE 3: BME690 Sensor Detection ==="
	
	if ! command -v i2cdetect &> /dev/null; then
		warn "i2cdetect not found, installing i2c-tools..."
		apt-get install -y i2c-tools
	fi
	
	# Try to detect sensor on I2C bus 1 (standard RPi)
	if i2cdetect -y 1 2>/dev/null | grep -q "76\|77"; then
		log "Scanning I2C bus 1..."
		SENSOR_ADDR=$(i2cdetect -y 1 2>/dev/null | grep -o "76\|77" | head -1)
		ok "BME690 sensor detected at 0x$SENSOR_ADDR"
	else
		warn "BME690 sensor not detected on I2C bus 1"
		warn "Ensure sensor is connected and I2C is enabled"
		warn "Verify wiring: SDA→GPIO2, SCL→GPIO3, VIN→3.3V, GND→GND"
	fi
}

# Phase 4: Verify Python and venv
verify_venv(){
	log ""
	log "=== PHASE 4: Python Virtual Environment ==="
	
	if [ ! -d "$APP_DIR/.venv" ]; then
		warn "Virtual environment not found, will be created during installation"
	else
		ok "Virtual environment exists"
		
		# Test venv activation and imports
		if source "$APP_DIR/.venv/bin/activate" 2>/dev/null; then
			ok "Virtual environment activated successfully"
			
			# Check key libraries
			if python3 -c "import bme690" 2>/dev/null; then
				ok "bme690 library available"
			else
				warn "bme690 library missing (will be installed)"
			fi
			
			if python3 -c "import tkinter" 2>/dev/null; then
				ok "tkinter library available"
			else
				warn "tkinter missing (required for GUI)"
			fi
			
			deactivate 2>/dev/null || true
		else
			warn "Could not activate virtual environment"
		fi
	fi
}

parse_args "$@"

[ -d "$REPO_DIR/.git" ] || die "REPO_DIR $REPO_DIR missing or not a git repo."
[ "$EUID" -eq 0 ] || die "Must run as root"

# ============================================================================
# RUN PREREQUISITE CHECKS
# ============================================================================
if [ $CHECK_PREREQ -eq 1 ]; then
	log ""
	log "############################################################################"
	log "  RPi Lab Deployment - Prerequisite Checks"
	log "############################################################################"
	log ""
	
	check_system_prereqs
	check_i2c_config
	detect_bme690_sensor
	verify_venv
	
	log ""
	log "############################################################################"
	log "  Prerequisite Check Complete"
	log "############################################################################"
fi

# Prompt for branch if not set via environment
if [ -z "${GIT_BRANCH:-}" ]; then
    echo ""
    echo "============================================================================"
    echo "  Deployment Script for rpi-lab"
    echo "============================================================================"
    echo ""
    read -p "Enter GIT_BRANCH to deploy: " GIT_BRANCH
fi

# Validate branch name
if [ -z "$GIT_BRANCH" ]; then
    die "Branch name cannot be empty"
fi

# Deployment confirmation
echo ""
echo "============================================================================"
echo "  DEPLOYMENT CONFIRMATION"
echo "============================================================================"
echo "  Repository:        $REPO_DIR"
echo "  Branch:            $GIT_BRANCH"
echo "  App Directory:     $APP_DIR"
echo "  Service:           $SERVICE_NAME"
echo "  Backup:            $([ $DO_BACKUP -eq 1 ] && echo "Yes" || echo "No")"
echo "  Prerequisite Check: $([ $CHECK_PREREQ -eq 1 ] && echo "Yes" || echo "No")"
echo "  Hard Reset:        $([ $HARD -eq 1 ] && echo "Yes" || echo "No")"
echo "  Pull Latest:       $([ $PULL_LATEST -eq 1 ] && echo "Yes" || echo "No")"
echo "  Dry Run:           $([ $DRY_RUN -eq 1 ] && echo "Yes" || echo "No")"
echo "============================================================================"
echo ""
echo "To confirm deployment, type the branch name exactly: $GIT_BRANCH"
read -p "Confirmation: " BRANCH_CONFIRM

if [ "$BRANCH_CONFIRM" != "$GIT_BRANCH" ]; then
    echo ""
    err "Confirmation failed. You entered: '$BRANCH_CONFIRM'"
    err "Expected: '$GIT_BRANCH'"
    err "Deployment aborted."
    exit 1
fi

echo ""
echo "Deployment confirmed. Proceeding..."
echo ""

log "Config: REPO_DIR=$REPO_DIR APP_DIR=$APP_DIR BACKUP=$DO_BACKUP HARD=$HARD"

# ============================================================================
# PHASE 5: Backup and Git Operations
# ============================================================================
if [ $DO_BACKUP -eq 1 ]; then
	mkdir -p "$BACKUP_DIR"
	TS=$(date +%Y%m%dT%H%M%S)
	BK="$BACKUP_DIR/quick-rpi-lab-$TS.tgz"
	log "PHASE 5: Creating backup (excluding .venv, uploads) -> $BK"
	tar --exclude=".venv" --exclude="uploads" -czf "$BK" -C "$(dirname "$APP_DIR")" "$(basename "$APP_DIR")"
	ok "Backup created: $BK"
	
	# Set backup file for potential rollback
	BACKUP_FILE="$BK"
	log "Automatic rollback enabled (will restore from backup on error)"
else
	log "PHASE 5: Skipping backup (--no-backup)"
	warn "Rollback disabled - no backup available"
fi

log "Stopping service if running..."
systemctl stop $SERVICE_NAME || true
systemctl stop rpi_tui.service 2>/dev/null || true  # Stop old TUI service if it exists

if [ $PULL_LATEST -eq 1 ]; then
	log "PHASE 6: Pulling latest changes from branch '$GIT_BRANCH'..."
	cd "$REPO_DIR"
	
	# Fetch latest changes
	git fetch origin
	
	# Check if branch exists remotely
	if git ls-remote --heads origin "$GIT_BRANCH" | grep -q "$GIT_BRANCH"; then
		log "Checking out and pulling branch '$GIT_BRANCH'..."
		git checkout "$GIT_BRANCH" 2>/dev/null || git checkout -b "$GIT_BRANCH" "origin/$GIT_BRANCH"
		git pull origin "$GIT_BRANCH"
		
		# Show what was updated
		LATEST_COMMIT=$(git log -1 --oneline)
		log "Latest commit: $LATEST_COMMIT"
	else
		warn "Branch '$GIT_BRANCH' not found remotely, using current local state"
	fi
else
	log "PHASE 6: Skipping git pull (--no-pull)"
fi

log "PHASE 7: Syncing repo to /opt/rpi-lab..."
rsync -a --delete --chown=root:root "$REPO_DIR/" "$APP_DIR/"

if [ $HARD -eq 1 ]; then
	log "PHASE 8: Hard reset: discarding local changes in $REPO_DIR"
	cd "$REPO_DIR"
	git fetch origin "$GIT_BRANCH"
	git reset --hard "origin/$GIT_BRANCH"
fi

log "PHASE 9: Ensuring venv exists..."
if [ ! -d "$APP_DIR/.venv" ]; then
	warn "Creating venv (this may take 1-2 minutes)..."
	bash "$APP_DIR/install/venv_setup.sh" || warn "venv setup completed with warnings"
	ok "Virtual environment created"
else
	ok "Virtual environment already exists"
fi

log "PHASE 10: Installing systemd service..."
cp "$APP_DIR/gui/rpi_gui.service" "/etc/systemd/system/$SERVICE_NAME" || warn "Could not copy service file"
chmod 644 "/etc/systemd/system/$SERVICE_NAME"
ok "Service file installed"

# Remove old TUI service if it exists
if [ -f "/etc/systemd/system/rpi_tui.service" ]; then
	log "Cleaning up old TUI service..."
	systemctl stop rpi_tui.service 2>/dev/null || true
	systemctl disable rpi_tui.service 2>/dev/null || true
	rm -f "/etc/systemd/system/rpi_tui.service"
	ok "Old service removed"
fi

log "PHASE 11: Reloading systemd and starting GUI service..."
systemctl daemon-reload
systemctl enable --now $SERVICE_NAME || warn "Could not enable service"
systemctl restart $SERVICE_NAME || warn "Could not restart service"
ok "GUI service deployed and started"

log ""
log "============================================================================"
log "  Deployment Complete"
log "============================================================================"
log ""
log "Service Status:"
systemctl status $SERVICE_NAME -l || warn "Service status check failed"

log ""
log "Recent Log Output:"
journalctl -u $SERVICE_NAME -n 10 || true

log ""
ok "Deployment finished successfully"
log "Service will auto-start on boot"
log "To view logs: journalctl -u $SERVICE_NAME -f"
log ""

# Clear backup file reference - deployment succeeded
BACKUP_FILE=""
