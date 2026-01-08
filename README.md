# RPI Lab

**Comprehensive Raspberry Pi monitoring & control system** with environmental sensing, RF monitoring, and audio alerts.

## Overview

RPI Lab provides an integrated platform for:
- **Environmental Monitoring** — BME690 sensor (temperature, humidity, pressure, gas)
- **Touch GUI** — Waveshare 4.3" 800×480 display with large buttons
- **SSH Monitoring** — TUI interface for remote access via convenient aliases
- **TPMS Monitoring** — Real-time tire pressure sensors via CC1101 RF transceiver
- **Audio Alerts** — PWM speaker notifications for environmental thresholds
- **Safe Deployment** — Git-based updates with prerequisite checking & auto-rollback

**Current Version:** v3.0.7 | **Updated:** 2026-01-09

## Quick Start (10 minutes)

```bash
# 1. Update Pi and install prerequisites
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip rsync

# 2. Clone repository
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab

# 3. Copy to /opt and run installers
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh         # Python virtualenv + deps
sudo /opt/rpi-lab/install/display_install.sh    # Waveshare display + touch
sudo /opt/rpi-lab/install/install_gui.sh        # GUI mode + auto-start
sudo reboot
```

## Documentation Index

Complete documentation is organized in the `docs/` folder:

| Topic | File | Purpose |
|-------|------|---------|
| **Installation** | [docs/INSTALLATION.md](docs/INSTALLATION.md) | Detailed setup for all components |
| **GUI Features** | [docs/GUI.md](docs/GUI.md) | Touch interface, buttons, displays |
| **TUI Setup** | [docs/TUI_SETUP.md](docs/TUI_SETUP.md) | SSH monitoring & alias setup |
| **BME690 Sensor** | [docs/BME690.md](docs/BME690.md) | I2C wiring, setup, testing |
| **TPMS Monitor** | [docs/TPMS_MONITORING.md](docs/TPMS_MONITORING.md) | Tire pressure monitoring |
| **Deployment** | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | GitHub workflow, deploy scripts |
| **Service Mgmt** | [docs/SERVICE_MANAGEMENT.md](docs/SERVICE_MANAGEMENT.md) | Systemd service control |
| **Troubleshooting** | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & fixes |
| **Hardware** | [docs/HARDWARE_WIRING.md](docs/HARDWARE_WIRING.md) | Pin assignments & connectors |

## Key Features

### 🎨 Touch GUI (v3.0.4+)
- Real-time network info (IP, gateway, DNS)
- Sensor display (temperature, humidity, pressure, gas)
- 7-level gas heater status with color indicators
- System buttons (TPMS, speaker test, reboot, terminal, exit)
- Auto-start on boot via systemd service

### 📟 SSH Monitoring (v3.0.5+)

The easiest way to access TUI is via aliases (already set up):

```bash
ssh user@pi-ip
rpi-tui              # Full sensor + RF display
rpi-tui-sensor       # Sensor only
rpi-tui-rf           # RF/TPMS only
```

**To set up aliases manually:**
```bash
echo "alias rpi-tui='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py'" >> ~/.bash_aliases
echo "alias rpi-tui-sensor='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --sensor'" >> ~/.bash_aliases
echo "alias rpi-tui-rf='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --rf'" >> ~/.bash_aliases
source ~/.bash_aliases
```

See [docs/TUI_SETUP.md](docs/TUI_SETUP.md) for complete details.

### 🔊 Smart Audio Alerts
- **Gas Detection**: Beep every 15 seconds when < 5kΩ (Red level only)
- **Temperature**: Hourly when < 0°C or > 30°C
- **Humidity**: Hourly when < 25% or > 80%
- **System Events**: Startup, shutdown, reboot notifications

### 🌡️ BME690 Sensor
- I2C interface (address 0x76)
- Real-time readings: temperature, humidity, pressure, gas resistance
- 7-level gas heater status tracking
- Exponential backoff for I2C reliability

### 🚗 TPMS RF Monitor
- CC1101 transceiver (433 MHz)
- Real-time tire pressure monitoring
- Supplier identification (Schrader, Continental)
- CSV/JSON data logging

### 🔧 Safe Deployment
- Interactive branch selection
- Automatic backup & rollback
- Prerequisite checking (Python, I2C, sensors)
- Clear progress output

## Repository Structure

```
rpi-lab/
├── gui/                       # GUI and TUI applications
│   ├── rpi_gui.py            # Touch GUI (tkinter)
│   ├── rpi_tui.py            # SSH TUI (rich)
│   ├── rpi_gui.service       # Systemd service
│   └── tpms_monitor_gui.py   # TPMS application
├── sensors/                  # Sensor libraries
│   ├── bme690.py             # BME690 wrapper
│   └── speaker.py            # PWM speaker control
├── rf/                       # RF transceiver code
│   ├── setup_pi.sh           # RF hardware setup
│   ├── tpms_decoder.py       # TPMS packet decoder
│   └── CC1101/               # CC1101 driver
├── deploy/                   # Deployment scripts
│   ├── deploy.sh             # Full deployment
│   └── quick_deploy.sh       # Fast updates
├── install/                  # Installation scripts
│   ├── venv_setup.sh         # Python virtualenv
│   ├── display_install.sh    # Display + touch
│   ├── install_gui.sh        # GUI auto-start
│   └── install_rf.sh         # RF hardware
├── docs/                     # Detailed documentation
│   ├── INSTALLATION.md
│   ├── GUI.md
│   ├── TUI_SETUP.md
│   ├── BME690.md
│   ├── TPMS_MONITORING.md
│   ├── DEPLOYMENT.md
│   ├── SERVICE_MANAGEMENT.md
│   ├── TROUBLESHOOTING.md
│   └── HARDWARE_WIRING.md
└── README.md                 # This file
```

## Gas Heater Status Levels

| Level | Range | Status | Color |
|-------|-------|--------|-------|
| 1 | < 5kΩ | 🔴 Gas Detected | Red |
| 2 | 5-10kΩ | 🟠 Warm-Up | Orange |
| 3 | 10-20kΩ | 🟡 Stabilizing | Yellow |
| 4 | 20-40kΩ | �� Cont. Stab. | Bright Yellow |
| 5 | 40-60kΩ | 🟢 Further Stab. | Light Green |
| 6 | 60-100kΩ | 🟢 Stabilized | Green |
| 7 | > 100kΩ | ✓ Normal | Bright Green |

**Note:** Audio alerts only trigger at level 1 (Gas Detected, < 5kΩ) every 15 seconds.

## Common Commands

### GUI Service
```bash
sudo systemctl status rpi_gui.service    # Check status
sudo systemctl restart rpi_gui.service   # Restart
sudo journalctl -u rpi_gui.service -f    # View logs
```

### TUI (SSH Monitoring)
```bash
ssh user@pi-ip
rpi-tui-sensor                           # Sensor only
rpi-tui --interval 1.0                   # Custom refresh
```

### Deployment
```bash
# Fast update
sudo bash /opt/rpi-lab/deploy/quick_deploy.sh

# Full deployment with safety checks
sudo bash /opt/rpi-lab/deploy/deploy.sh
```

### I2C & Sensor Verification
```bash
i2cdetect -y 1                           # List I2C devices
sudo systemctl status rpi_gui.service    # Check sensor init
```

## Requirements

### Hardware
- **Raspberry Pi** 4/5 (3B+ may work)
- **Waveshare 4.3" DSI LCD Rev 2.2** (800×480 touch display)
- **BME690 Sensor** (I2C, address 0x76)
- **CC1101 RF Transceiver** (optional, for TPMS)
- **PWM Speaker** (GPIO 12, 3.3V tolerant)

### Software
- **OS:** Raspberry Pi OS Bookworm/Trixie
- **Python:** 3.9+
- **Dependencies:** See [requirements.txt](requirements.txt)

## Troubleshooting

Quick fixes for common issues:

| Issue | Solution |
|-------|----------|
| **GUI won't start** | Check X11: `ps aux \| grep Xorg` |
| **No touch response** | Run `sudo /opt/rpi-lab/display/test_touch.sh` |
| **Sensor not detected** | Run `i2cdetect -y 1` and verify address 0x76 |
| **TUI aliases missing** | Run `source ~/.bash_aliases` or restart SSH session |
| **Deployment hangs** | Check internet and run `sudo /opt/rpi-lab/deploy/deploy.sh -h` |

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for comprehensive troubleshooting.

## Contributing

Contributions welcome! Suggested workflow:

```bash
git checkout -b feat/your-change
# Make edits...
git add -A && git commit -m "feat: describe change"
git push origin feat/your-change
# Open PR on GitHub
```

## License

See [LICENSE](LICENSE) file.

## Support

- **Issues:** GitHub Issues on this repository
- **Docs:** See [docs/](docs/) folder for detailed guides
- **Logs:** `journalctl -u rpi_gui.service -f`

---

**Last Updated:** 2026-01-09 | **Version:** v3.0.7 | **Maintained by:** mrmagicbg
