# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2025-12-22
### Added
- **TPMS (Tire Pressure Monitoring System) Support**
  - New `rf/tpms_decoder.py` module with Schrader and Siemens/VDO protocol decoders
  - Manchester bit-level decoding for RF packets
  - Automatic pressure (kPa/PSI) and temperature (°C/°F) conversion
  - Battery status and signal quality indicators
  
- **TPMS Monitor GUI** (`rf/tpms_monitor_gui.py`)
  - Real-time RF capture and visualization
  - Live sensor cards showing pressure, temperature, battery, RSSI
  - Start/Stop capture controls
  - Activity log with packet details
  - Automatic sensor ID tracking and updates
  
- **CC1101 RF Tools Integration**
  - Built `rx_profile_demo` binary for TPMS mode (433.92 MHz)
  - CSV packet logging with timestamp and decoded fields
  - Support for IoT, GFSK, OOK modes
  
- **Comprehensive Documentation**
  - `docs/TPMS_MONITORING.md` - Complete TPMS guide
  - Protocol specifications (Schrader, Siemens/VDO)
  - Hardware wiring diagrams
  - Troubleshooting guide
  - Security and legal notes

### Changed
- **Main GUI Enhancement**
  - RF button now launches TPMS Monitor GUI (was terminal script)
  - Button renamed to "📡 TPMS Monitor" for clarity
  - Integrated launch from main control panel
  
- **RF Setup Script**
  - Successfully builds rx_profile_demo with WiringPi
  - Added TPMS mode compilation and testing

### Fixed
- Exit button confirmed present and working in main GUI
- RF tools compilation on Raspberry Pi 3B
- SPI interface enabled and tested

## [0.3.1] - 2025-12-22
### Changed
- **GUI Layout Redesign**
  - All touch buttons now uniform size for consistent touch experience
  - Sensor readings moved to main screen (auto-updates every 5 seconds)
  - Temperature and humidity displayed prominently above buttons
  - 4 main buttons: RF Script, Reboot, Terminal, Exit (all same size)
  - Improved visual hierarchy and touch targets

- **Installation Scripts**
  - Updated `venv_setup.sh` to install system dependencies for DHT22 (python3-dev, build-essential)
  - Added automatic Adafruit-DHT installation with --force-pi flag
  - Better error handling and progress messages

### Fixed
- Sensor readings now update automatically without button press
- Exit button always visible on main screen
- Consistent button sizing eliminates touch target confusion

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

