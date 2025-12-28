#!/usr/bin/env bash
# deploy.sh - Safe redeployment script for rpi-lab
#
# This script safely redeploys rpi-lab from GitHub to /opt/rpi-lab
# with backup creation, venv management, and service restart.
#
# Features:
# - Safety confirmation prompts (requires typing branch name)
# - Automatic backup creation with timestamps
# - Smart repository detection from script location
# - Virtual environment recreation
# - Git branch pulling with latest changes
# - Systemd service management (GUI mode)
#
# Usage: sudo bash deploy.sh [OPTIONS]
# Options:
#   --no-backup    Skip creating backup before deployment
#   --hard         Force git reset --hard to remote branch (discards local changes)
#   --no-pull      Skip pulling latest changes from remote branch
#   --dry-run      Show what would be done without making changes
#
# Environment Variables:
#   DEPLOY_BRANCH  Branch to deploy (if set, skips prompt; otherwise prompts with main default)
#   APP_DIR        Target application directory (defaults to /opt/rpi-lab)
#   BACKUP_DIR     Backup directory (defaults to /opt/backups)
#
# Examples:
#   sudo bash deploy.sh                          # Prompts for branch (defaults to main)
#   sudo bash deploy.sh --no-backup              # Skip backup creation
#   sudo bash deploy.sh --hard                   # Force reset local changes
#   sudo bash deploy.sh --no-pull                # Deploy current local state
#   DEPLOY_BRANCH=main sudo bash deploy.sh      # Deploy specific branch without prompting
set -euo pipefail
IFS=$'\n\t'

# Determine REPO_DIR from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="${APP_DIR:-/opt/rpi-lab}"
SERVICE_NAME="rpi_gui.service"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups}"
DO_BACKUP=1
HARD=0
# DEPLOY_BRANCH will be set from environment or prompted for
DRY_RUN=0
PULL_LATEST=1

COLOR_RED='\033[0;31m'; COLOR_GRN='\033[0;32m'; COLOR_YLW='\033[0;33m'; COLOR_BLU='\033[0;34m'; COLOR_RST='\033[0m'
log(){ echo -e "${COLOR_BLU}➤${COLOR_RST} $*"; }
ok(){ echo -e "${COLOR_GRN}✓${COLOR_RST} $*"; }
warn(){ echo -e "${COLOR_YLW}⚠${COLOR_RST} $*"; }
err(){ echo -e "${COLOR_RED}✗${COLOR_RST} $*"; }
die(){ err "$*"; exit 1; }

parse_args(){
	while [ $# -gt 0 ]; do
		case "$1" in
			--no-backup) DO_BACKUP=0 ;;
			--dry-run) DRY_RUN=1 ;;
			--hard) HARD=1 ;;
			--no-pull) PULL_LATEST=0 ;;
			*) die "Unknown arg: $1" ;;
		esac
		shift
	done
}

parse_args "$@"

[ -d "$REPO_DIR/.git" ] || die "REPO_DIR $REPO_DIR missing or not a git repo."
[ "$EUID" -eq 0 ] || die "Must run as root"

# Prompt for branch if not set via environment
if [ -z "${DEPLOY_BRANCH:-}" ]; then
    echo ""
    echo "============================================================================"
    echo "  Deployment Script for rpi-lab"
    echo "============================================================================"
    echo ""
    read -p "Enter branch to deploy [main]: " DEPLOY_BRANCH
    DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
fi

# Validate branch name
if [ -z "$DEPLOY_BRANCH" ]; then
    die "Branch name cannot be empty"
fi

# Deployment confirmation
echo ""
echo "============================================================================"
echo "  DEPLOYMENT CONFIRMATION"
echo "============================================================================"
echo "  Repository:        $REPO_DIR"
echo "  Branch:            $DEPLOY_BRANCH"
echo "  App Directory:     $APP_DIR"
echo "  Service:           $SERVICE_NAME"
echo "  Backup:            $([ $DO_BACKUP -eq 1 ] && echo "Yes" || echo "No")"
echo "  Hard Reset:        $([ $HARD -eq 1 ] && echo "Yes" || echo "No")"
echo "  Pull Latest:       $([ $PULL_LATEST -eq 1 ] && echo "Yes" || echo "No")"
echo "  Dry Run:           $([ $DRY_RUN -eq 1 ] && echo "Yes" || echo "No")"
echo "============================================================================"
echo ""
echo "To confirm deployment, type the branch name exactly: $DEPLOY_BRANCH"
read -p "Confirmation: " BRANCH_CONFIRM

if [ "$BRANCH_CONFIRM" != "$DEPLOY_BRANCH" ]; then
    echo ""
    err "Confirmation failed. You entered: '$BRANCH_CONFIRM'"
    err "Expected: '$DEPLOY_BRANCH'"
    err "Deployment aborted."
    exit 1
fi

echo ""
echo "Deployment confirmed. Proceeding..."
echo ""

log "Config: REPO_DIR=$REPO_DIR APP_DIR=$APP_DIR BACKUP=$DO_BACKUP HARD=$HARD"

if [ $DO_BACKUP -eq 1 ]; then
	mkdir -p "$BACKUP_DIR"
	TS=$(date +%Y%m%dT%H%M%S)
	BK="$BACKUP_DIR/quick-rpi-lab-$TS.tgz"
	log "Creating backup (excluding .venv, uploads) -> $BK"
	tar --exclude=".venv" --exclude="uploads" -czf "$BK" -C "$(dirname "$APP_DIR")" "$(basename "$APP_DIR")"
	ok "Backup created: $BK"
fi

log "Stopping service if running..."
systemctl stop $SERVICE_NAME || true
systemctl stop rpi_tui.service 2>/dev/null || true  # Stop old TUI service if it exists

if [ $PULL_LATEST -eq 1 ]; then
	log "Pulling latest changes from branch '$DEPLOY_BRANCH'..."
	cd "$REPO_DIR"
	
	# Fetch latest changes
	git fetch origin
	
	# Check if branch exists remotely
	if git ls-remote --heads origin "$DEPLOY_BRANCH" | grep -q "$DEPLOY_BRANCH"; then
		log "Checking out and pulling branch '$DEPLOY_BRANCH'..."
		git checkout "$DEPLOY_BRANCH" 2>/dev/null || git checkout -b "$DEPLOY_BRANCH" "origin/$DEPLOY_BRANCH"
		git pull origin "$DEPLOY_BRANCH"
		
		# Show what was updated
		LATEST_COMMIT=$(git log -1 --oneline)
		log "Latest commit: $LATEST_COMMIT"
	else
		warn "Branch '$DEPLOY_BRANCH' not found remotely, using current local state"
	fi
fi

log "Syncing repo to /opt/rpi-lab..."
rsync -a --delete --chown=root:root "$REPO_DIR/" "$APP_DIR/"

if [ $HARD -eq 1 ]; then
	log "Hard reset: discarding local changes in $REPO_DIR"
	cd "$REPO_DIR"
	git fetch origin "$DEPLOY_BRANCH"
	git reset --hard "origin/$DEPLOY_BRANCH"
fi

log "Ensuring venv exists..."
if [ ! -d "$APP_DIR/.venv" ]; then
	bash "$APP_DIR/install/venv_setup.sh"
fi

log "Copying systemd unit file..."
cp "$APP_DIR/gui/rpi_gui.service" "/etc/systemd/system/$SERVICE_NAME"
chmod 644 "/etc/systemd/system/$SERVICE_NAME"

# Remove old TUI service if it exists
if [ -f "/etc/systemd/system/rpi_tui.service" ]; then
	log "Removing old TUI service..."
	systemctl stop rpi_tui.service 2>/dev/null || true
	systemctl disable rpi_tui.service 2>/dev/null || true
	rm -f "/etc/systemd/system/rpi_tui.service"
fi

log "Reloading systemd and restarting GUI service..."
systemctl daemon-reload
systemctl enable --now $SERVICE_NAME
systemctl restart $SERVICE_NAME
ok "GUI service deployed and restarted."

log "Status:"
systemctl status $SERVICE_NAME -l
