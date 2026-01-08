# Deployment Guide

GitHub-based deployment workflow for RPI Lab.

## Initial Setup (One-Time)

### 1. SSH Keys on Pi

```bash
# Copy your GitHub SSH key to Pi
scp ~/.ssh/id_ed25519_* user@pi-ip:~/.ssh/

# Configure SSH for GitHub
ssh user@pi-ip
cat >> ~/.ssh/config << 'SSHCONF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
SSHCONF

# Test connection
ssh -T git@github.com
```

### 2. Configure Git Remote

```bash
ssh user@pi-ip
cd /opt/rpi-lab
sudo git remote set-url origin git@github.com:user/rpi-lab.git
```

## Daily Workflow

### On Development Machine

```bash
cd ~/Code/rpi-lab

# Make changes
vim gui/rpi_gui.py

# Test locally
python3 -m py_compile gui/rpi_gui.py

# Commit and push
git add .
git commit -m "feat: add feature"
git push origin main
```

### Deploy to Pi

#### Quick Deploy (Fast)

For minor updates:

```bash
ssh user@pi-ip
sudo /opt/rpi-lab/deploy/quick_deploy.sh
```

**What it does:**
- Stops GUI service
- Pulls latest from GitHub
- Updates Python dependencies if needed
- Restarts GUI service

#### Full Deploy (Safe)

For major updates or first deployment:

```bash
ssh user@pi-ip
sudo /opt/rpi-lab/deploy/deploy.sh
```

**What it does:**
- Validates prerequisites (Python, I2C, sensor)
- Creates timestamped backup
- Pulls latest changes
- Syncs to /opt/rpi-lab
- Recreates virtual environment
- Restarts services
- Shows deployment status

#### Deploy Options

```bash
sudo /opt/rpi-lab/deploy/deploy.sh --no-backup    # Skip backup
sudo /opt/rpi-lab/deploy/deploy.sh --hard         # Force reset
sudo /opt/rpi-lab/deploy/deploy.sh --no-pull      # Deploy local state
sudo /opt/rpi-lab/deploy/deploy.sh -h             # Show help
```

## Verification

```bash
# Check service status
sudo systemctl status rpi_gui.service

# View logs
sudo journalctl -u rpi_gui.service -n 20

# Test sensor
i2cdetect -y 1

# Monitor live
ssh user@pi-ip
rpi-tui-sensor
```

## Rollback

If deployment fails:

```bash
# List backups
ls -lh /opt/backups/

# Restore backup
sudo rm -rf /opt/rpi-lab
sudo cp -a /opt/backups/rpi-lab-backup-YYYYMMDD-HHMMSS /opt/rpi-lab
sudo systemctl restart rpi_gui.service
```

## Branch Strategy

- **main** - Production (on Pi)
- **dev** - Development/testing
- **feature/*** - New features
- **hotfix/*** - Quick fixes

Deploy specific branch:

```bash
GIT_BRANCH=dev sudo /opt/rpi-lab/deploy/deploy.sh
```

## Deployment Checklist

- [ ] Changes tested locally
- [ ] Committed and pushed to GitHub
- [ ] Deployment script selected (quick vs full)
- [ ] Service restarted successfully
- [ ] GUI displays correctly
- [ ] Sensor readings accurate
- [ ] No errors in logs
- [ ] TUI accessible via SSH

## Common Issues

**Deployment hangs:**
- Check internet connection
- Verify GitHub SSH access
- Check disk space: `df -h`

**Service won't start:**
- Check logs: `journalctl -u rpi_gui.service -f`
- Verify Python venv: `ls /opt/rpi-lab/.venv/`
- Test X11: `ps aux | grep Xorg`

**Sensor not working:**
- Verify I2C: `i2cdetect -y 1`
- Check wiring
- Confirm user in i2c group: `groups`

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.
