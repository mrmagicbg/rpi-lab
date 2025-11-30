# RPI Lab

Overview
--------

RPI Lab collects small utilities and helpers targeting Raspberry Pi devices:

- `rf/` — RF-related code and Pi setup for CC1101 projects
- `display/` — Display and touchscreen setup scripts (Waveshare panels)
- `tui/` — Console (TUI) application and systemd service that runs on boot

This README provides a Quickstart, detailed install steps, troubleshooting and maintenance guidance for deploying the project on a Raspberry Pi.

Table of Contents
-----------------

- Quickstart
- Installation (detailed)
- Service management
- Touch testing & debugging
- Troubleshooting
- Contributing

Quickstart (10 minutes)
-----------------------

1) Update the Pi and install prerequisites:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip rsync
```

2) Clone the repo into your home directory (developer mode):

```bash
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
```

3) Optional: move to `/opt` for system-wide installs and run the helpers:

```bash
sudo mkdir -p /opt/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/install_service.sh
```

Or use the deployment script for full redeployment (recommended):

```bash
sudo bash ~/rpi-lab/deploy/deploy.sh
```

The deployment script includes safety features:
- Prompts for branch confirmation to prevent accidental deployments
- Creates backups of existing installations
- Supports dry-run mode for testing
- Handles venv recreation and service restarts

Installation (detailed)
-----------------------

See the `install/` folder for small helper scripts that setup the virtualenv (`venv_setup.sh`), display drivers (`display_install.sh`) and service installation (`install_service.sh`). Typical steps:

1. Prepare the Pi and install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip
```

2. Clone and copy into `/opt` (optional):

```bash
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
```

3. Run the helper scripts (provided under `install/`):

```bash
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/display_install.sh    # display + touch
sudo /opt/rpi-lab/install/install_rf.sh         # RF hardware setup (optional)
sudo /opt/rpi-lab/install/install_service.sh    # install and enable TUI systemd unit
```

Or use the deployment script for full redeployment (recommended for updates):

```bash
sudo bash /opt/rpi-lab/deploy/deploy.sh [--no-backup] [--hard] [--dry-run]
```

**Deployment Script Features:**
- **Safety Prompts**: Requires branch name confirmation to prevent accidental deployments
- **Automatic Backups**: Creates timestamped backups before making changes
- **Flexible Options**: 
  - `--no-backup`: Skip backup creation
  - `--hard`: Force git reset to remote branch (discards local changes)
  - `--dry-run`: Show what would be done without making changes
- **Smart Repo Detection**: Automatically finds repo location from script path
- **Service Management**: Handles systemd reload and service restart

Service management
------------------

The TUI runs as a systemd service defined in `tui/rpi_tui.service` and defaults to running on `tty1`.

Common commands:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rpi_tui.service
sudo systemctl status rpi_tui.service -l
sudo journalctl -xeu rpi_tui.service --no-pager
```

If you change the unit file, run `sudo systemctl daemon-reload` before restarting or enabling.

Touch testing & debugging
-------------------------

Install `evtest` to inspect input events:

```bash
sudo apt-get update
sudo apt-get install -y evtest
sudo evtest /dev/input/event0
```

Run the TUI directly to see debug output (inside the venv):

```bash
source /opt/rpi-lab/.venv/bin/activate
sudo /opt/rpi-lab/.venv/bin/python /opt/rpi-lab/tui/rpi_tui.py
```

**Touch Debugging Features:**
- The TUI logs detailed touch coordinate information
- Shows raw touch values, scaled coordinates, and button mapping
- Helps diagnose touch calibration and button position issues
- Check logs with: `sudo journalctl -xeu rpi_tui.service --no-pager`

Troubleshooting
---------------

Git corruption (`object file .git/objects/<xx>/<hash> is empty`):

```bash
cd ~/rpi-lab
# Backup .git
cp -a .git ../rpi-lab-git-backup-$(date +%s)
# Move the broken object out of the way
mv .git/objects/<xx>/<hash> /tmp/
git fsck --full
git fetch --all
git fetch --prune --all
git pull

# Fallback: reclone and rsync working tree
cd ..
git clone https://github.com/mrmagicbg/rpi-lab.git rpi-lab-recovered
rsync -av --exclude='.git' rpi-lab/ rpi-lab-recovered/
```

Service start failures (tty or permissions):

- Check `sudo journalctl -xeu rpi_tui.service` for Python tracebacks or permission errors.
- Verify the virtualenv path `/opt/rpi-lab/.venv/bin/python` exists.
- If the service can't access `/dev/tty1`, consider running the unit as `root` (default) or adjust `User=` and group/device permissions.

Contributing
------------

Contributions welcome. Suggested workflow:

```bash
git checkout -b feat/your-change
make your edits
git add -A
git commit -m "Describe change"
git push origin feat/your-change
# Open a PR on GitHub
```

If you'd like me to add an automated repair script (`install/repair_git.sh`) or make other doc improvements, tell me which pieces to prioritize.
