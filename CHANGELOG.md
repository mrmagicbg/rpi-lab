# Changelog

Recent releases. Full history in [docs/CHANGELOG_ARCHIVE.md](docs/CHANGELOG_ARCHIVE.md).

## [3.0.9] - 2026-01-09
**MQTT Integration for Home Assistant - Complete Implementation**

### Added
- BME690 MQTT Publisher for Home Assistant integration
  - Auto-discovery with device info (identifiers, model, manufacturer)
  - Real-time sensor publishing: temperature, humidity, pressure, gas resistance
  - JSON payloads with ISO timestamps
  - Exponential backoff reconnection logic (5 attempts, up to 80s delay)
  - Signal handlers (SIGTERM/SIGINT) for graceful shutdown
  - Systemd service with restart policy and i2c group access

- Installation script: `install/install_mqtt.sh`
  - Interactive configuration prompts for MQTT broker details
  - Dynamic path updates for service file (WorkingDirectory, ExecStart)
  - Automatic service enable and start
  - User detection for systemd service configuration
  - Cleanup of temporary/invalid package installations

- Comprehensive documentation: `docs/HOME_ASSISTANT_MQTT.md`
  - Home Assistant setup (Mosquitto broker add-on installation)
  - Port forwarding configuration (1883/8883)
  - Security recommendations (TLS, VPN, reverse proxy options)
  - Troubleshooting guide with common issues
  - Home Assistant automation examples
  - HA dashboard card examples

### Fixed
- Library package: `pimoroni-bme680` → `bme680==2.0.0` (correct PyPI package)
- Import module: `bme690` → `bme680` (correct Pimoroni library)
- Service configuration with proper paths
- BME690 sensor initialization with error handling
- Deploy script prerequisite checking (dpkg-query instead of dpkg -l)
- Deploy script exit on missing packages (set -e pipefail issue)
- MQTT client callback API v1 deprecation warning

### Dependencies Added
- `paho-mqtt==1.6.1` - MQTT client library
- `bme680==2.0.0` - BME680/690 sensor library (Pimoroni)

### Testing & Deployment Notes
- Virtual environment must be recreated: `sudo python3 -m venv /opt/rpi-lab/.venv --system-site-packages`
- All requirements must install in production venv (`/opt/rpi-lab/.venv`), not development (`~/rpi-lab/.venv`)
- Service expects: `/opt/rpi-lab/.venv/bin/python3` executable
- Use `install_mqtt.sh` to configure MQTT connection interactively
- Test with: `sudo journalctl -u mqtt_publisher.service -f`
- Expected log: "Published: T=XX.X°C, H=XX.X%, P=XXXX.XhPa, G=XXXXXXΩ"

### See Also
- [docs/HOME_ASSISTANT_MQTT.md](docs/HOME_ASSISTANT_MQTT.md) - Complete HA integration guide
- [sensors/mqtt_publisher.py](sensors/mqtt_publisher.py) - Publisher implementation
- [sensors/mqtt_publisher.service](sensors/mqtt_publisher.service) - Systemd service file
- [install/install_mqtt.sh](install/install_mqtt.sh) - Installation script

## [3.0.8] - 2026-01-09
- Documentation consolidation and cleanup
- Minimal root README with links to docs/
- Created docs/TUI_SETUP.md with alias instructions

## [3.0.7] - 2026-01-08
- Added TUI bash aliases (rpi-tui, rpi-tui-sensor, rpi-tui-rf)

## [3.0.6] - 2026-01-08
- Gas alerts only trigger at < 5kΩ (was 50kΩ)

## [3.0.5] - 2026-01-08
- Added TUI for SSH monitoring
- Enhanced gas label with status text

## [3.0.4] - 2026-01-08
- Gas heater status with 7 color levels
- Deploy script help (-h/--help)

## [3.0.3] - 2026-01-08
- Fixed BME690 dry-run mode
- Fixed TPMS decoder syntax error

## [3.0.2] - 2026-01-08
- Updated bme690 to 1.0.0, smbus2 to 0.6.0

## [3.0.1] - 2026-01-08
- Fixed deployment hanging
- Fixed RF compilation errors

---

See [docs/CHANGELOG_ARCHIVE.md](docs/CHANGELOG_ARCHIVE.md) for detailed history.
