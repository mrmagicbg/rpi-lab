# Changelog

Recent releases. Full history in [docs/CHANGELOG_ARCHIVE.md](docs/CHANGELOG_ARCHIVE.md).

## [3.0.13] - 2026-01-11
**Deployment Script Improvements**

### Fixed
- Deployment script now installs and restarts **both** GUI and MQTT publisher services
  - Previously only `rpi_gui.service` was restarted after deployment
  - Now `mqtt_publisher.service` is also installed/restarted automatically
  - Both services show status at deployment completion

### Changed
- Enhanced deployment status output to show both services
- Both services now auto-start on boot after deployment

## [3.0.12] - 2026-01-11
**Gas Heater Disabled by Default**

### Changed
- **BME690_ENABLE_GAS now defaults to 0 (disabled)** for improved humidity accuracy
  - Gas heater warming effect causes 10-30%RH underreporting
  - Gas readings no longer available by default
  - To re-enable: set `BME690_ENABLE_GAS=1` in environment or .env file
  - Improves humidity accuracy from ~37%RH to actual ambient levels

### Notes
- If you need gas/air quality readings, explicitly set `BME690_ENABLE_GAS=1`
- This change prioritizes humidity accuracy over gas sensing
- After upgrading, expect humidity readings to increase by 10-30%RH

## [3.0.11] - 2026-01-11
**BME690/BME688 Pressure Reading Bugfix**

### Fixed
- **CRITICAL:** Pressure readings corrected from 4.33x too high to accurate values
  - Root cause: bme680 library v2.0.0 pressure calculation bug with BME688 chip
  - Hardware: Pimoroni BME690 breakout (uses BME688 sensor chip ID 0x61, variant 0x02)
  - Applied correction factor: `pressure = pressure_raw / 4.33`
  - Readings now ~1013 hPa (correct) instead of ~4391 hPa (incorrect)
  - Affects all display outputs: GUI, TUI, MQTT

### Added
- Diagnostic scripts for sensor troubleshooting:
  - `sensors/test_sensor_readings.py` - comprehensive sensor value testing
  - `sensors/check_chip_id.py` - chip identification (BME280 vs BME680 vs BME688)

### Notes
- If upgrading from v3.0.10 or earlier, pressure values will change significantly
- Update any automations that rely on pressure thresholds
- Normal sea-level pressure: ~1013 hPa (was incorrectly showing ~4391 hPa)

## [3.0.10] - 2026-01-11
**BME690 Humidity Calibration & Gas Heater Control**

### Added
- Environment variable controls for BME690 sensor accuracy tuning:
  - `BME690_ENABLE_GAS=0` : Disable gas heater to improve humidity accuracy
  - `BME690_HUM_SCALE=1.0` : Humidity scaling factor (multiplicative)
  - `BME690_HUM_OFFSET=0.0` : Humidity offset in %RH (additive)
- Humidity calibration: `final = (raw * scale + offset)` clamped to 0-100%RH
- Enhanced logging for gas heater status and calibration application
- Improved module docstring with environment variable documentation
- Test script: `sensors/test_humidity_calibration.py` for finding optimal calibration

### Fixed
- Humidity readings consistently lower than GUI/reference meters
  - Root cause: BME680/690 gas heater warms sensor, reducing humidity readings
  - Solution: Optional heater disable or calibration compensation
- TUI and MQTT now reflect same corrected humidity values as GUI

### Changed
- BME690 initialization now logs gas heater state (enabled/disabled)
- Humidity calibration logged at INFO level during init, DEBUG during reads
- Module docstring expanded with calibration usage examples
- **MQTT Publisher:** Gas resistance now published in kΩ (was Ω) for better HA display
- **MQTT Discovery:** Gas resistance unit changed to kΩ in auto-discovery config

### Notes
- To match reference meter: set `BME690_ENABLE_GAS=0` and restart services
- For fine-tuning: adjust `BME690_HUM_OFFSET` in small increments (e.g., +5, +10)
- Set env vars in service files for persistence (see docs/SERVICE_MANAGEMENT.md)
- Gas resistance now matches TUI display format (kΩ instead of Ω)

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
