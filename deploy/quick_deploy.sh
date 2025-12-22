#!/usr/bin/env bash
# quick_deploy.sh - Fast deployment script for rpi-lab updates
#
# This script pulls latest changes from GitHub and restarts the GUI service.
# Use this for quick updates when you've already committed and pushed changes.
#
# Usage: 
#   On local machine: git push origin main
#   On Pi: sudo bash /opt/rpi-lab/deploy/quick_deploy.sh
#
# Or run remotely:
#   ssh 10.10.10.105 "sudo bash /opt/rpi-lab/deploy/quick_deploy.sh"

set -euo pipefail

APP_DIR="/opt/rpi-lab"
SERVICE_NAME="rpi_gui.service"
VENV_DIR="$APP_DIR/.venv"
REQ_FILE="$APP_DIR/requirements.txt"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}RPI Lab Quick Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}✗ Please run as root: sudo $0${NC}"
  exit 1
fi

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
  echo -e "${RED}✗ App directory not found: $APP_DIR${NC}"
  exit 1
fi

cd "$APP_DIR"

# Stop service before updating
echo -e "${YELLOW}→ Stopping $SERVICE_NAME...${NC}"
systemctl stop "$SERVICE_NAME" || true

# Pull latest changes from GitHub
echo -e "${YELLOW}→ Pulling latest changes from GitHub...${NC}"
git fetch origin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "  Current branch: ${BLUE}$CURRENT_BRANCH${NC}"

# Show what's new
BEHIND=$(git rev-list HEAD..origin/$CURRENT_BRANCH --count 2>/dev/null || echo "0")
if [ "$BEHIND" -gt 0 ]; then
  echo -e "  ${YELLOW}$BEHIND commits behind origin/$CURRENT_BRANCH${NC}"
  git --no-pager log HEAD..origin/$CURRENT_BRANCH --oneline --decorate --max-count=5
else
  echo -e "  ${GREEN}Already up to date${NC}"
fi

git pull origin "$CURRENT_BRANCH"
echo -e "${GREEN}✓ Code updated${NC}"

# Update virtual environment if requirements changed
if [ -f "$REQ_FILE" ]; then
  echo -e "${YELLOW}→ Updating Python dependencies...${NC}"
  if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip -q
    pip install -r "$REQ_FILE" -q
    echo -e "${GREEN}✓ Dependencies updated${NC}"
  else
    echo -e "${RED}✗ Virtual environment not found at $VENV_DIR${NC}"
    echo -e "${YELLOW}  Creating new virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip -q
    pip install -r "$REQ_FILE"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
  fi
fi

# Restart service
echo -e "${YELLOW}→ Starting $SERVICE_NAME...${NC}"
systemctl daemon-reload
systemctl start "$SERVICE_NAME"

# Wait a moment for service to start
sleep 2

# Check service status
if systemctl is-active --quiet "$SERVICE_NAME"; then
  echo -e "${GREEN}✓ Service started successfully${NC}"
else
  echo -e "${RED}✗ Service failed to start${NC}"
  echo -e "${YELLOW}  Checking logs:${NC}"
  journalctl -u "$SERVICE_NAME" -n 20 --no-pager
  exit 1
fi

echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo "Service status:"
systemctl status "$SERVICE_NAME" --no-pager -l | head -10
echo
echo "To view logs: journalctl -u $SERVICE_NAME -f"
