# Changelog Archive

Detailed version history for reference. See [root CHANGELOG.md](../CHANGELOG.md) for recent releases.

## [3.0.7] - 2026-01-09

### Added - TUI Aliases & Documentation Consolidation
- Convenient bash aliases for quick TUI access via SSH:
  - `rpi-tui` — Full interface (both sensor and RF panels)
  - `rpi-tui-sensor` — Sensor data only
  - `rpi-tui-rf` — RF/TPMS data only
- Aliases added to `~/.bash_aliases` on Pi for persistence across sessions
- Consolidated documentation structure:
  - Single README.md in root with documentation index
  - Single CHANGELOG.md in root with recent changes
  - Detailed docs in docs/ folder (INSTALLATION, GUI, TUI_SETUP, etc.)

### Docs
- Updated README with TUI alias information and quick-start guide
- Created docs/TUI_SETUP.md with complete alias setup instructions
- Added manual alias setup procedure for users who need it
- Troubleshooting section for common TUI alias issues
- Documentation index in README pointing to docs/ folder

## [3.0.6] - 2026-01-08

### Changed - Gas Alert Threshold
- Gas alert beeping now only triggers for "Gas Detected" level (< 5kΩ)
- Previous threshold of 50kΩ caused false alerts during normal warm-up
- Beeping remains at 15-second intervals when true gas detection occurs
- Other gas status levels (Warm-Up through Normal) display without audio alerts
- Updated alert documentation to reflect new behavior

## [3.0.5] - 2026-01-08

### Added - TUI Interface & Enhanced Gas Display
- **TUI (Text User Interface)** (`gui/rpi_tui.py`)
  - SSH-accessible real-time monitoring interface using rich library
  - Color-coded gas heater status display with 7 levels
  - Sensor data panel showing temperature, humidity, pressure, gas
  - RF/TPMS data panel (placeholder for future integration)
  - Multiple display modes: --sensor, --rf, --both
  - Configurable refresh interval (default: 2 seconds)
  - Perfect for headless monitoring and remote debugging
  
- **Enhanced Gas Label** (`gui/rpi_gui.py`)
  - Gas label now shows status text with ohms value
  - Abbreviated status names for compact display
  - Examples: "Warm-Up (8.5 kΩ)", "Stabilizing (15.2 kΩ)", "Normal (125.3 kΩ)"
  - Consistent with full status display below sensor readings

### Changed
- Gas label font reduced to 12pt for better fit with status text
- Gas container uses sticky='w' for proper left alignment
- Separate function `get_gas_label_text()` for abbreviated status display

## [3.0.4] - 2026-01-08

### Added - Gas Heater Status Indicators
- **GUI Enhancements** (`gui/rpi_gui.py`)
  - Added real-time gas heater status display with color-coded indicators
  - Gas heater status shows current state with resistance value in kΩ
  - 7 distinct status levels:
    - ⚠️ Gas Detected (< 5kΩ) - Red
    - 🔥 Initial Warm-Up (5-10kΩ) - Orange
    - ⏳ Stabilizing (10-20kΩ) - Yellow
    - 📈 Continued Stabilization (20-40kΩ) - Light Yellow
    - 🔄 Further Stabilization (40-60kΩ) - Light Green
    - ✅ Stabilized (60-100kΩ) - Green
    - ✓ Normal Operation (> 100kΩ) - Dark Green
  - Status text now uses consistent font size (10pt) with other GUI elements
  - Separate display for last update time and gas heater status
  
- **Deployment Script** (`deploy/deploy.sh`)
  - Added comprehensive help documentation (-h/--help)
  - Usage examples for common deployment scenarios
  - All deployment phases documented
  - Troubleshooting section with recovery instructions

### Changed
- Gas heater status is now prominently displayed below sensor readings
- Status updates reflect real-time air quality conditions
- Visual feedback helps understand sensor stabilization process

## [3.0.3] - 2026-01-08

### Fixed - BME690 Real Sensor & TPMS Monitor
- **Service Configuration** (`gui/rpi_gui.service`)
  - Removed `BME690_DRY_RUN=1` environment variable
  - Sensor now uses real hardware instead of simulated values
  - Accurate temperature, humidity, pressure, and gas readings from BME690
  
- **TPMS Monitor** (`rf/tpms_decoder.py`)
  - Fixed Python syntax error: missing closing quote in TPMSDecoder docstring
  - Fixed IndentationError that prevented TPMS monitor GUI from launching
  - TPMS monitor button now works correctly

### Changed
- BME690 sensor now reports real values from hardware at I2C address 0x76
- Gas resistance readings reflect actual air quality (typically 5-200kΩ depending on conditions)
- Gas alerts will trigger during heater warm-up period (first ~5 minutes after startup)

## [3.0.2] - 2026-01-08

### Fixed - Python Dependencies
- **Requirements** (`requirements.txt`)
  - Updated bme690 library version from 0.3.2 to 1.0.0 (latest available on PyPI/piwheels)
  - Updated smbus2 library version from 0.5.2 to 0.6.0 (0.5.2 not available)
  - Fixed "ModuleNotFoundError: No module named 'bme690'" error on fresh deployments
  - Ensures BME690 sensor works properly instead of falling back to dry-run mode

## [3.0.1] - 2026-01-08

### Fixed - Deployment & Compilation Issues
- **Deployment Script** (`deploy/deploy.sh`)
  - Added root user verification with clear error message
  - Added DEBIAN_FRONTEND=noninteractive for non-interactive apt-get
  - Reduced apt-get verbosity with -qq flags
  - Improved error handling and logging
  
- **RF Setup Script** (`rf/setup_pi.sh`)
  - Fixed directory navigation bug causing "directory not found" during RF compilation
  - Changed WiringPi installation to save/restore current directory
  - Prevents "cd" errors when setup path contains spaces or special characters

### Changed
- Deployment now handles edge cases with better error recovery
- Verbose logging helps diagnose deployment issues
- More reliable package installation with automatic formatting

---

## Version Numbering

- **Major (3.x.x):** Major features or breaking changes
- **Minor (x.0.x):** New features, enhancements
- **Patch (x.x.1+):** Bug fixes, dependency updates

## Branch Strategy

- **main:** Stable releases (what's on Pi in production)
- **dev:** Development branch with features under testing
- **feature/*:** Feature branches for new functionality
- **hotfix/*:** Quick fixes for production issues
