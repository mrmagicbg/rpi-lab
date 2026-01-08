# RPI Lab

Overview
--------

RPI Lab is a comprehensive Raspberry Pi monitoring and control system with integrated hardware support for environmental sensing, RF monitoring, and audio alerts:

- **`sensors/`** — **BME690 environmental sensor** (temperature, humidity, pressure, gas) with **PWM speaker alerts**
- **`gui/`** — **Touch-friendly GUI** with network info, sensor display, alerts, and system controls
- **`rf/`** — **TPMS tire pressure monitoring** with CC1101 RF transceiver (433 MHz)
- **`display/`** — Display and touchscreen setup scripts (Waveshare 4.3" DSI Rev 2.2)
- **`deploy/`** — GitHub-based deployment with branch selection and automatic rollback

### Key Features

✨ **Enhanced GUI** (v3.0.0)
- Real-time network information (IP/mask, gateway, DNS servers)
- BME690 sensor monitoring with compact 2x2 grid display
- Intelligent audio alerts for environmental thresholds
- Test speaker button for audio verification
- Full-screen touch-optimized interface (800x480)

🔊 **Smart Audio Alerts**
- **Gas detection**: Beep every 15 seconds when volatile gases detected
- **Temperature**: Hourly alerts when < 0°C or > 30°C
- **Humidity**: Hourly alerts when < 25% or > 80%
- **System events**: Startup, shutdown, and reboot notifications
- Hardware PWM for clean, consistent audio (GPIO 12)

🌡️ **BME690 Environmental Sensor**
- Temperature (°C), humidity (%RH), pressure (hPa), gas resistance (Ω)
- I2C interface (0x76 primary, 0x77 secondary)
- Gas heater stabilization with status indicators
- Exponential backoff retry for I2C reliability

🚗 **TPMS RF Monitor**
- Real-time tire pressure monitoring via CC1101 transceiver
- Multi-sensor support with live data visualization
- Standalone GUI with packet capture controls

📡 **Network Monitoring**
- IP address with CIDR notation (e.g., 192.168.1.100/24)
- Default gateway and DNS server display
- Auto-detection of eth0/wlan0 interfaces
- Updates every 30 seconds

🔧 **Deployment & Maintenance**
- Interactive branch selection with confirmation
- Automatic backup before deployment
- Rollback on failure
- Comprehensive prerequisite checking
- Aligned with IGW deployment patterns

This README provides Quickstart, detailed install steps, hardware wiring, sensor configuration, troubleshooting and maintenance guidance for deploying the project on a Raspberry Pi.

Table of Contents
-----------------

- Quickstart
- Installation (detailed)
- GUI Features
- TPMS RF Monitor
- BME690 Sensor Setup
- GitHub Deployment Workflow
- Service management
- Touch testing & debugging
- Display + touch: known-good configuration (Waveshare 4.3" DSI Rev 2.2)
- Troubleshooting
- Contributing

Quickstart (10 minutes)
-----------------------

1) Update the Pi and install prerequisites:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip rsync
```

2) Clone the repo into your home directory:

```bash
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
```

3) Copy to `/opt` for system-wide install and run the helpers:

```bash
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh         # Python virtualenv + dependencies
sudo /opt/rpi-lab/install/display_install.sh    # Waveshare display + touch
sudo /opt/rpi-lab/install/install_gui.sh        # GUI mode with auto-start
sudo reboot
```

Or use the deployment script for full redeployment:

```bash
sudo bash ~/rpi-lab/deploy/deploy.sh
```

Installation (detailed)
-----------------------

See the `install/` folder for helper scripts:
- `venv_setup.sh` — Python virtualenv + dependencies (evdev, rich, loguru, bme690)
- `display_install.sh` — Waveshare 4.3" DSI LCD Rev 2.2 display + touch overlays
- `install_gui.sh` — **GUI mode** (X11, openbox, python3-tk, auto-login)
- `install_rf.sh` — RF hardware setup for CC1101

### GUI Mode Installation

1. Prepare the Pi and install system packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip rsync
```

2. Clone and copy into `/opt`:

```bash
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
```

3. Run the helper scripts:

```bash
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/display_install.sh    # Waveshare 4.3" DSI Rev 2.2 display + touch
sudo /opt/rpi-lab/install/install_gui.sh         # GUI mode with large touch buttons
```

4. Reboot to start GUI on boot:

```bash
sudo reboot
```

### Quick Updates via GitHub Deployment (v3.0.0)

The deployment script now follows IGW patterns with interactive branch selection:

```bash
# On the Pi: run deployment script
sudo bash /opt/rpi-lab/deploy/deploy.sh

# You'll be prompted for:
# 1. Branch name to deploy (e.g., main, dev, feature/xyz)
# 2. Confirmation (type exact branch name to proceed)
```

**Environment Variable Option** (skip prompts):
```bash
# Deploy specific branch without prompting
GIT_BRANCH=main sudo bash /opt/rpi-lab/deploy/deploy.sh
```

**Deployment Features**:
- ✅ Interactive branch selection with confirmation
- ✅ Automatic backup before deployment
- ✅ Rollback on failure
- ✅ Comprehensive prerequisite checking (I2C, sensor, packages)
- ✅ Service status verification
- ✅ Clear phase-based progress output

**Options**:
```bash
sudo bash /opt/rpi-lab/deploy/deploy.sh --no-backup   # Skip backup
sudo bash /opt/rpi-lab/deploy/deploy.sh --hard        # Force reset local changes
sudo bash /opt/rpi-lab/deploy/deploy.sh --no-pull     # Deploy current local state
sudo bash /opt/rpi-lab/deploy/deploy.sh --dry-run     # Show what would be done
```

GUI Features
------------

The GUI application provides an intuitive touch interface optimized for the Waveshare 4.3" 800×480 display:

### Layout (v3.0.0 Enhanced)

**Integrated Info Panel** (top section):
- **Network Info** (left): IP/mask (CIDR), gateway, DNS servers
- **Sensor Data** (right): Temperature, humidity, pressure, gas resistance (2x2 grid)
- Auto-updates every 5-30 seconds
- Status line shows update time, I2C status, gas heater stability

**5 Uniform Touch Buttons** (bottom section):
- **📡 TPMS Monitor** - Launch RF tire pressure monitoring GUI (Blue)
- **🔊 Test Speaker** - Play test beep pattern for audio verification (Orange)
- **🔄 Reboot System** - System reboot with confirmation dialog (Red)
- **💻 Open Terminal** - Launch xterm terminal window (Green)
- **❌ Exit Application** - Close GUI with confirmation (Gray)

### Design Features

- **Unified Info Display**: Network and sensor data side-by-side for quick reference
- **Smart Audio Alerts**: Beeps for gas, temperature, humidity thresholds + system events
- **Uniform Touch Targets**: All buttons identical size for consistent touch experience
- **Persistent Data**: All critical info always visible (no popups needed)
- **Auto-Refresh**: Network (30s) and sensor (5s) update intervals
- **Color-Coded Interface**: Different colors help identify button functions quickly
- **Confirmation Dialogs**: Destructive actions (reboot, exit) require confirmation
- **Fullscreen Mode**: F11 to toggle, Escape to exit (keyboard shortcuts)
- **Auto-start**: Launches automatically on boot via systemd service

TPMS RF Monitor
---------------

Real-time tire pressure monitoring system using CC1101 RF transceiver.

### Features

- **Live Sensor Display**: Shows all detected TPMS sensors with individual cards
- **Pressure Monitoring**: Displays pressure in both PSI and kPa with status indicators
  - **CRITICAL** (red): < 26 PSI
  - **LOW** (orange): 26-28 PSI
  - **NORMAL** (green): 28-44 PSI
  - **HIGH** (yellow): > 44 PSI
- **Temperature Display**: Shows tire temperature in °C and °F
- **Battery Status**: Indicates low/critical battery warnings from sensors with visual alerts
- **Signal Quality**: RSSI assessment with quality indicators (Excellent/Good/Fair/Poor)
- **Supplier Information**: Identifies sensor manufacturer (Schrader, Siemens/Continental)
- **Data Export**: Session-based CSV and JSON logging with summary statistics
- **Protocol Support**: 
  - Schrader (EG53MA4, G4) - 433.92 MHz
  - Siemens/VDO (Continental) - 433.92 MHz
  - Generic Manchester-encoded TPMS

### Hardware Setup

**CC1101 Module Wiring**:
```
CC1101 Pin    → Raspberry Pi GPIO
VCC (3.3V)    → Pin 1 (3.3V)
GND           → Pin 6 (GND)
MOSI          → Pin 19 (GPIO 10)
MISO          → Pin 21 (GPIO 9)
SCK           → Pin 23 (GPIO 11)
CSN           → Pin 24 (GPIO 8, CE0)
GDO0          → Pin 22 (GPIO 25)
ANT           → 17.3 cm wire (433 MHz quarter-wave)
```

**Enable SPI**:
```bash
sudo raspi-config
# → Interface Options → SPI → Yes
```

**Build RF Tools**:
```bash
sudo bash /opt/rpi-lab/install/install_rf.sh
```

### Usage

1. **From Main GUI**: Click "📡 TPMS Monitor" button
2. **Standalone**: `python /opt/rpi-lab/rf/tpms_monitor_gui.py`
3. **Click "Start Capture"** to begin monitoring
4. **Trigger sensors**: Drive vehicle or use TPMS activation tool
5. **View results**: Sensor cards appear showing pressure, temp, battery, and supplier info

**Data Logging**:
- All sessions are automatically logged to `~/rpi-lab/logs/tpms/`
- Export formats: CSV and JSON
- Summary statistics included (min/max/avg values)

**Full Documentation**: See [`docs/TPMS_MONITORING.md`](docs/TPMS_MONITORING.md)

BME690 Sensor Setup & Audio Alerts
-----------------------------------

The RPI Lab uses the Pimoroni **BME690** breakout for environmental sensing with intelligent audio alerts.

### Hardware Wiring

**BME690 Sensor Connections**:

| BME690 | Raspberry Pi Pin | Description |
|--------|-------------------|-------------|
| VCC    | Pin 1 (3.3V)      | Power |
| SDA    | Pin 3 (GPIO2)     | I2C Data |
| SCL    | Pin 5 (GPIO3)     | I2C Clock |
| GND    | Pin 6 (GND)       | Ground |

**PWM Speaker Connections**:

| Speaker Wire | Raspberry Pi Pin | Description |
|--------------|------------------|-------------|
| Red (+)      | Pin 32 (GPIO12)  | Hardware PWM output |
| Black (-)    | Pin 6 or 9 (GND) | Ground |

**Complete Hardware Guide**: [`docs/HARDWARE_WIRING.md`](docs/HARDWARE_WIRING.md)

### Enable I2C and Verify Sensor

```bash
sudo raspi-config
# → Interface Options → I2C → Enable → Reboot

# Verify sensor detection
i2cdetect -y 1
# Should show '76' at address 0x76
```

### Software Installation

Handled by `install/venv_setup.sh` and `requirements.txt` (includes `bme690` and `RPi.GPIO`):

```bash
sudo /opt/rpi-lab/install/venv_setup.sh
```

### Testing Sensor & Speaker

**Dry-run (no hardware)**:

```bash
cd /opt/rpi-lab
source .venv/bin/activate
export BME690_DRY_RUN=1
export SPEAKER_DRY_RUN=1
python3 sensors/bme690.py
python3 sensors/speaker.py
```

**Hardware test**:

```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 sensors/bme690.py     # Test BME690 sensor
python3 sensors/speaker.py    # Test speaker patterns
```

### Audio Alert System (New in v3.0.0)

The GUI provides intelligent audio alerts using hardware PWM on GPIO 12:

**Alert Conditions**:
- **🫁 Volatile Gas Detection**: Double beep every 15 seconds when gas resistance < 50kΩ
  - Indicates VOCs, smoke, cooking fumes, etc.
- **🌡️ Temperature Alerts**: Triple beep hourly when < 0°C or > 30°C
- **💧 Humidity Alerts**: Double beep hourly when < 25% or > 80%
- **🔊 System Events**:
  - Startup: Long beep when GUI launches
  - Shutdown: Long beep when GUI exits
  - Reboot: Triple beep before system reboot
- **🎵 Test**: Press "🔊 Test Speaker" button in GUI for audio verification

**Alert Features**:
- **Throttling**: Gas alerts every 15 seconds, temp/humidity hourly
- **Non-blocking**: Background thread processing
- **Hardware PWM**: Clean 2000 Hz square wave (no jitter)
- **Configurable**: Thresholds in `gui/rpi_gui.py`

**To disable alerts**:
```bash
# Set environment variable before starting GUI
export SPEAKER_DRY_RUN=1
```

### Network Information Display (New in v3.0.0)

The GUI shows real-time network status:
- **IP Address**: With CIDR notation (e.g., 192.168.1.100/24)
- **Gateway**: Default gateway IP
- **DNS Servers**: Up to 2 nameservers
- **Auto-detection**: eth0 first, falls back to wlan0
- **Refresh**: Every 30 seconds

### Sensor Features

**Gas Heater Stabilization**:
- Initial warm-up: ~5 minutes for first accurate gas reading
- "Gas heater stable" indicator when ready
- Air quality estimation: Good > 150kΩ, Moderate 50-150kΩ, Poor 10-50kΩ, Very Poor < 10kΩ

**Error Recovery**:
- Exponential backoff on I2C errors (5s → 15s → 60s)
- Automatic recovery when sensor reconnects
- Error counter with retry countdown

**Data Logging**:
```bash
# View real-time logs
journalctl -u rpi_gui.service -f

# Check alert history
journalctl -u rpi_gui.service | grep -i "alert"
```

### GUI Integration

- Displays temperature, humidity, pressure, gas resistance
- Network info panel (IP, gateway, DNS)
- Status line with update time and gas heater stability
- Fullscreen auto-start on boot via `rpi_gui.service`

GitHub Deployment Workflow
---------------------------

### Initial Setup

1. **Configure SSH keys** (one-time setup on Pi):

```bash
# Copy your SSH keys to Pi
scp ~/.ssh/id_ed25519_mrmagicbg* 10.10.10.105:~/.ssh/

# Configure SSH for GitHub
ssh 10.10.10.105 "cat >> ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_mrmagicbg
    StrictHostKeyChecking no
EOF"

# Test GitHub connection
ssh 10.10.10.105 "ssh -T git@github.com"
```

2. **Configure git remote** for SSH:

```bash
ssh 10.10.10.105 "cd /opt/rpi-lab && sudo git remote set-url origin git@github.com:mrmagicbg/rpi-lab.git"
```

### Daily Workflow

**Development → Deploy → Test**

1. **On your development machine:**

```bash
cd ~/Code/GitHub/mrmagicbg/rpi-lab

# Make changes to code
vim gui/rpi_gui.py

# Test locally (optional)
python3 -m py_compile gui/rpi_gui.py

# Commit and push
git add .
git commit -m "feat: add new feature"
git push origin main
```

2. **On the Raspberry Pi (or remotely):**

```bash
# Option A: SSH and run quick deploy
ssh 10.10.10.105 "sudo bash /opt/rpi-lab/deploy/quick_deploy.sh"

# Option B: Full deployment with safety checks
ssh 10.10.10.105 "sudo bash /opt/rpi-lab/deploy/deploy.sh"
```

3. **Verify deployment:**

```bash
ssh 10.10.10.105 "systemctl status rpi_gui.service"
ssh 10.10.10.105 "journalctl -u rpi_gui.service -n 20"
```

### Deployment Scripts

#### quick_deploy.sh (Recommended for Updates)

Fast deployment for incremental changes:

```bash
sudo bash /opt/rpi-lab/deploy/quick_deploy.sh
```

**What it does:**
- Stops GUI service
- Pulls latest changes from GitHub
- Shows commits behind origin
- Updates Python dependencies if requirements.txt changed
- Restarts GUI service
- Displays service status

**Use when:** Making frequent updates, testing changes

#### deploy.sh (Full Deployment with Prerequisite Checking)

Comprehensive deployment with validation and safety features:

```bash
sudo bash /opt/rpi-lab/deploy/deploy.sh
```

**What it does:**
- **Phase 1:** Validates system prerequisites (python3, venv, i2c-tools, etc.)
- **Phase 2:** Checks I2C kernel modules and configuration
- **Phase 3:** Detects BME690 sensor on I2C bus (0x76/0x77)
- **Phase 4:** Verifies Python virtual environment and libraries
- **Phase 5:** Creates timestamped backup (with automatic rollback on failure)
- **Phases 6-11:** Git pull, rsync, venv creation, service installation, restart

**New in v2.0:**
- ✓ Comprehensive prerequisite checking before deployment
- ✓ Colored status output (✓ success, ⚠ warning, ✗ error)
- ✓ I2C sensor detection with address reporting
- ✓ Automatic rollback on deployment failure
- ✓ Python library validation (bme690, tkinter)

**Options:**
```bash
sudo bash deploy.sh --no-backup     # Skip backup (faster, no rollback)
sudo bash deploy.sh --no-prereq     # Skip prerequisite checking
sudo bash deploy.sh --hard          # Force git reset --hard
sudo bash deploy.sh --no-pull       # Skip git pull (deploy local state)
```

**Use when:** Major updates, first-time deployment, troubleshooting

**Example output:**
```
=== PHASE 1: System Prerequisites ===
✓ python3 installed
✓ python3-venv installed
✓ i2c-tools installed
Status: 6 installed, 0 missing

=== PHASE 2: I2C Configuration ===
✓ I2C kernel modules loaded
✓ I2C device files exist

=== PHASE 3: BME690 Sensor Detection ===
✓ BME690 sensor detected at 0x76

=== PHASE 4: Python Virtual Environment ===
✓ Virtual environment exists
✓ bme690 library available
✓ tkinter library available

[Deployment proceeds safely...]
```

### Rollback

If deployment fails, restore from backup:

```bash
# List backups
ls -lh /opt/backups/

# Restore specific backup
sudo rm -rf /opt/rpi-lab
sudo cp -a /opt/backups/rpi-lab-backup-YYYYMMDD-HHMMSS /opt/rpi-lab
sudo systemctl restart rpi_gui.service
```

Service management
------------------

### GUI Service (rpi_gui.service)

Runs the GUI application in X11 after graphical.target.

**Service file location:** `/etc/systemd/system/rpi_gui.service`

**Common commands:**

```bash
# Enable and start service
sudo systemctl enable --now rpi_gui.service

# Check service status
sudo systemctl status rpi_gui.service -l

# View logs (live tail)
sudo journalctl -u rpi_gui.service -f

# View recent logs
sudo journalctl -u rpi_gui.service -n 50

# Restart service after code changes
sudo systemctl restart rpi_gui.service

# Reload systemd after editing service file
sudo systemctl daemon-reload
```

**Auto-start configuration:**
- Service starts after `graphical.target` and `network-online.target`
- 5-second delay to ensure X11 is ready
- Runs as user `mrmagic` with DISPLAY=:0
- Auto-restarts on failure with 10-second delay

**Troubleshooting service issues:**

```bash
# Check if X11 is running
ps aux | grep Xorg

# Check DISPLAY environment
echo $DISPLAY

# Check if LightDM is active
systemctl status lightdm

# View full service logs
journalctl -u rpi_gui.service --no-pager -b
```

Touch testing & debugging
-------------------------

Install `evtest` to inspect input events:

```bash
sudo apt-get update
sudo apt-get install -y evtest
sudo evtest /dev/input/event2  # ft5x06 touch device
```

Run the GUI directly for debug output:

```bash
source /opt/rpi-lab/.venv/bin/activate
DISPLAY=:0 /opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_gui.py
```

**Touch Debugging Features:**
- GUI logs all button presses and touch events
- Shows sensor readings and error messages
- Check logs with: `sudo journalctl -u rpi_gui.service -f`
- Test touch with: `sudo evtest /dev/input/event2`

**Common touch issues:**

1. **No touch response** - Check `/proc/bus/input/devices` for ft5x06
2. **Wrong coordinates** - Verify display overlay matches hardware (waveshare-800x480)
3. **Intermittent touch** - Check power supply, use polling_mode overlay
4. **Ghost touches** - Check for electrical interference, ground display properly

Display + touch: known-good configuration (Waveshare 4.3" DSI Rev 2.2)
-------------------------------------------------------------

For the Waveshare 4.3" DSI LCD Rev 2.2 panel with ft5x06 touch, the
project uses the following **tested working** configuration:

1. `config.txt` (Bookworm/Trixie images typically use `/boot/firmware/config.txt`):

  ```ini
  # Manually configure DSI display (disable auto-detect)
  display_auto_detect=0

  [all]
  # Waveshare 4.3" DSI LCD Rev 2.2 (800x480)
  dtoverlay=vc4-kms-dsi-waveshare-800x480

  # Touch controller (ft5x06) using polling mode to avoid IRQ timeout
  dtoverlay=edt-ft5406,polling_mode

  # Optional: 3D acceleration (comment out if instability occurs)
  dtoverlay=vc4-kms-v3d

  # Helpful when using KMS with multiple framebuffers
  max_framebuffers=2
  ```

2. Recommended setup commands (from a fresh Pi):

  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y git python3 python3-venv python3-pip rsync

  git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
  sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/

  # Python virtualenv + TUI deps (rich, loguru, evdev)
  sudo /opt/rpi-lab/install/venv_setup.sh

  # Waveshare 4.3" DSI Rev 2.2 display + touch + tools (evtest, i2c-tools)
  sudo /opt/rpi-lab/install/display_install.sh

  # Systemd service
  sudo /opt/rpi-lab/install/install_service.sh

  # Reboot to apply overlays and start the TUI on tty1
  sudo reboot
  ```

3. Post-install verification:

  ```bash
  # High-level check (overlays, fb0, backlight, touch, service)
  sudo /opt/rpi-lab/display/health_check.sh

  # Live touch events from ft5x06
  sudo /opt/rpi-lab/display/test_touch.sh

  # Kernel overlay list and touch driver
  sudo dtoverlay -l
  sudo dmesg | grep -i 'ft5\|edt'
  ```

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

Touch device detection failures (ft5x06 timeout):

- **Symptom:** `edt_ft5x06 10-0038: probe with driver edt_ft5x06 failed with error -110`
- **Cause:** IRQ-driven probe timing out on the ft5x06 interrupt line during driver probe
- **Primary fix (recommended):**
  - Run the Waveshare 4.3" installer, which applies the full known-good config:
    ```bash
    sudo /opt/rpi-lab/display/setup_waveshare_4.3inch_dsi.sh --reboot
    ```
    This ensures the display overlay and touch overlay are set to:
    - `dtoverlay=vc4-kms-dsi-waveshare-800x480`
    - `dtoverlay=edt-ft5406,polling_mode`

- **Secondary fix (touch only, if display is already correct):**
  - Normalize just the touch overlay to polling mode:
    ```bash
    sudo bash /opt/rpi-lab/display/fix_touch_detection.sh
    ```
    This guarantees there is a `dtoverlay=edt-ft5406,polling_mode` line in the
    active `config.txt`, allowing the device to be detected via polling instead
    of interrupts.

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

---

**Last updated:** 2026-01-01
