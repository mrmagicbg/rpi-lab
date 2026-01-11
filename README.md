# RPI Lab

Raspberry Pi monitoring system with BME690 sensor, touch GUI, SSH monitoring, and TPMS RF support.

## ⚠️ Important: BME680/688 Humidity Readings

**Hardware Note:** Pimoroni BME690 breakout contains **BME688 chip** (Bosch's newer version of BME680).
- Chip ID: 0x61 (BME688)
- All specs and behavior identical to BME680
- See [docs/BME680.pdf](docs/BME680.pdf) for official Bosch datasheet

**DO NOT disable the gas heater** - it's required for proper sensor operation and accuracy.

**If humidity readings seem low:**
- The sensor is likely **correct** (±3%RH accuracy per Bosch datasheet)
- Cheap reference sensors often read 10-20%RH **too high**
- Gas heater impact is only 1-3%RH, not 30%RH
- Verify against salt calibration test (NaCl saturated = 75%RH) before adjusting
- See [docs/BME680.pdf](docs/BME680.pdf) for official specs
- See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for calibration procedures

**Key finding:** 38%RH at 4.5°C is normal for winter indoor air. Don't "fix" accurate readings!

## Quick Start

```bash
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/display_install.sh
sudo /opt/rpi-lab/install/install_gui.sh
sudo reboot
```

## Features

- **Touch GUI** — 800×480 display with sensor data, network info, system controls
- **SSH TUI** — Remote monitoring via `rpi-tui` aliases
- **BME690 Sensor** — Temperature, humidity, pressure, gas (I2C 0x76)
- **Audio Alerts** — PWM speaker notifications for environmental thresholds
- **TPMS Monitor** — CC1101 RF transceiver for tire pressure sensors
- **Safe Deployment** — Git-based updates with auto-rollback

## Common Commands

```bash
# Service control
sudo systemctl status rpi_gui.service
sudo systemctl restart rpi_gui.service
sudo journalctl -u rpi_gui.service -f

# SSH monitoring (aliases auto-created)
ssh user@pi-ip
rpi-tui                    # Full display
rpi-tui-sensor             # Sensor only
rpi-tui --interval 1.0     # Custom refresh

# Deployment
sudo /opt/rpi-lab/deploy/quick_deploy.sh       # Fast update
sudo /opt/rpi-lab/deploy/deploy.sh             # Full deploy

# Hardware verification
i2cdetect -y 1             # Check BME690 at 0x76
```

## Documentation

All detailed documentation is in [`docs/`](docs/):

- [Installation Guide](docs/INSTALLATION.md)
- [GUI Features](docs/GUI.md)
- [TUI Setup & Aliases](docs/TUI_SETUP.md)
- [BME690 Sensor](docs/BME690.md)
- [TPMS Monitoring](docs/TPMS_MONITORING.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Service Management](docs/SERVICE_MANAGEMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Hardware Wiring](docs/HARDWARE_WIRING.md)

## Hardware Requirements

- Raspberry Pi 4/5
- Waveshare 4.3" DSI LCD (800×480)
- BME690 sensor (I2C)
- PWM speaker (GPIO 12)
- CC1101 RF module (optional, for TPMS)

## Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| GUI won't start | `ps aux \| grep Xorg` |
| No touch | `sudo /opt/rpi-lab/display/test_touch.sh` |
| Sensor missing | `i2cdetect -y 1` (check 0x76) |
| TUI alias not found | `source ~/.bash_aliases` |

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

## License

See [LICENSE](LICENSE)

---

**Version:** 3.0.8 | **Last Updated:** 2026-01-09
