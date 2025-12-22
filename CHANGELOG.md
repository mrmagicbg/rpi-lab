# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-12-22
### Added
- **DHT22 Temperature & Humidity Sensor Support**
  - New `sensors/` module with DHT22 sensor driver (`sensors/dht22.py`)
  - GUI "Sensor Readings" button displays temperature and humidity
  - Comprehensive DHT22 wiring documentation (`docs/DHT22_WIRING.md`)
  - Adafruit_DHT library added to requirements

- **GUI Mode Enhancements**
  - 5-button interface: RF Script, Sensor Readings, Reboot, Shell, Exit
  - Large touch-friendly buttons optimized for Waveshare 4.3" display
  - Sensor readings popup with refresh capability
  - Color-coded buttons for easy visual identification

- **GitHub-Based Deployment**
  - SSH key authentication configured for GitHub
  - `quick_deploy.sh` for fast updates from GitHub
  - Updated `deploy.sh` for GUI service management
  - Simplified deployment workflow: push to GitHub, pull on Pi

### Changed
- **TUI Mode Removed (Breaking Change)**
  - Deleted `tui/` directory and all TUI components
  - Removed `rpi_tui.service` (replaced with `rpi_gui.service`)
  - Removed `install/install_service.sh` (TUI installer)
  - Updated all scripts to reference GUI mode only
  - Consolidated requirements.txt to project root

- **Requirements Management**
  - Moved `tui/requirements.txt` to project root `requirements.txt`
  - Updated `venv_setup.sh` to use new requirements path
  - Added Adafruit_DHT for sensor support

### Fixed
- Display overlay configuration in install scripts
- Deployment script service name updated to `rpi_gui.service`
- Documentation references updated to remove TUI mode

## [0.2.1] - 2025-11-30
- Deployment script and documentation improvements; touch input fixes and install helper additions.

