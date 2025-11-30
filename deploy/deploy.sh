#!/usr/bin/env bash
# deploy.sh - Redeploy rpi-lab to /opt/rpi-lab safely and restart TUI service
# Usage: sudo bash deploy.sh [--no-backup] [--hard]
set -euo pipefail
IFS=$'\n\t'

# Determine REPO_DIR from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="${APP_DIR:-/opt/rpi-lab}"
SERVICE_NAME="rpi_tui.service"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups}"
DO_BACKUP=1
HARD=0
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
DRY_RUN=0

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
			*) die "Unknown arg: $1" ;;
		esac
		shift
	done
}

parse_args "$@"

[ -d "$REPO_DIR/.git" ] || die "REPO_DIR $REPO_DIR missing or not a git repo."
[ "$EUID" -eq 0 ] || die "Must run as root"

log "Config: REPO_DIR=$REPO_DIR APP_DIR=$APP_DIR BACKUP=$DO_BACKUP HARD=$HARD"

if [ $DO_BACKUP -eq 1 ]; then
	mkdir -p "$BACKUP_DIR"
	TS=$(date +%Y%m%dT%H%M%S)
	BK="$BACKUP_DIR/quick-rpi-lab-$TS.tgz"
	log "Creating backup (excluding .venv, uploads) -> $BK"
	tar --exclude=".venv" --exclude="uploads" -czf "$BK" -C "$(dirname "$APP_DIR")" "$(basename "$APP_DIR")"
	ok "Backup created: $BK"
fi

log "Stopping TUI service if running..."
systemctl stop $SERVICE_NAME || true

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
cp "$APP_DIR/tui/rpi_tui.service" "/etc/systemd/system/rpi_tui.service"
chmod 644 "/etc/systemd/system/rpi_tui.service"

log "Reloading systemd and restarting TUI service..."
systemctl daemon-reload
systemctl enable --now rpi_tui.service
systemctl restart rpi_tui.service
ok "TUI service deployed and restarted."

log "Status:"
systemctl status rpi_tui.service -l
