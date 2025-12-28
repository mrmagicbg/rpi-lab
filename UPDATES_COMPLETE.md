# RPI Lab BME690 Sensor - Update Summary

**Date**: December 28, 2025  
**Status**: ✅ Ready for Deployment (dry-run tested)  
**Scope**: Migration from DHT22 (GPIO) to Pimoroni BME690 (I2C)

---

## Overview

The project now uses the Pimoroni BME690 environmental sensor (temperature, humidity, pressure, gas) over I2C. Code, GUI, service, requirements and documentation have been updated accordingly.

## What Changed

### 1. Core Sensor Implementation

**File**: `sensors/bme690.py`

**Highlights**:
- `bme690` PyPI library integration
- I2C initialization (primary 0x76, fallback 0x77)
- Oversampling/filter defaults and gas heater profile
- Dry-run mode via `BME690_DRY_RUN=1` (simulated readings)
- Provides: `read()` and `read_formatted()`

### 2. Installation Scripts

**File**: `install/venv_setup.sh`
- Added `python3-smbus` and `i2c-tools` installation for I2C support

**File**: `install/install_gui.sh`
- Added automatic `i2c` group configuration for user `mrmagic`
- Sudoers remains configured for passwordless reboot

### 3. Service Configuration

**File**: `gui/rpi_gui.service`
- Switched to `SupplementaryGroups=i2c` for I2C access
- Added `Environment=BME690_DRY_RUN=1` for development

### 4. Dependencies

**File**: `requirements.txt`
- Added `bme690` and `smbus2`
- Removed `gpiozero`

### 5. Documentation

**Files**: `README.md`, `docs/BME690_SETUP.md`, `docs/BME690_WIRING.md`, `DOCUMENTATION_INDEX.md`
- Updated and consolidated to reflect BME690 wiring, setup, and testing
- Removed all DHT22 documentation files

---

## Installation Quick Start

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-full python3-dev build-essential git i2c-tools python3-smbus

# 2. Clone and copy to /opt
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/

# 3. Run installation scripts
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/display_install.sh
sudo /opt/rpi-lab/install/install_gui.sh

# 4. Enable I2C and test sensor (dry-run by default via service)
sudo raspi-config nonint do_i2c 0
cd /opt/rpi-lab
source .venv/bin/activate
python3 -m sensors.bme690

# 5. Reboot
sudo reboot
```

After reboot, GUI appears fullscreen with BME690 readings.

---

## Hardware Wiring

See: `docs/BME690_WIRING.md`

---

## Testing & Verification

### Sensor Direct Test
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 -m sensors.bme690
```

### GUI Verification (after hardware arrival)
- [ ] GUI appears on boot automatically (fullscreen)
- [ ] Temperature, humidity, pressure, gas resistance visible (no N/A)
- [ ] Status shows last update time and heater stability
- [ ] Readings update every 5 seconds

---

## Key Improvements

| Improvement | Before | After |
|------------|--------|-------|
| **Sensor** | DHT22 (temp, humidity) | BME690 (temp, humidity, pressure, gas) |
| **Bus** | GPIO (timing-sensitive) | I2C (robust, standard) |
| **Library** | Mixed/legacy | Pimoroni `bme690` (maintained) |
| **Permissions** | GPIO group | I2C group |
| **Testing** | Limited | Dry-run support for development |

---

## Files Modified Summary

### Core Code
- ✅ `sensors/bme690.py` - New BME690 module with dry-run
- ✅ `requirements.txt` - Updated dependencies
- ✅ `gui/rpi_gui.py` - Updated to display BME690 readings

### Installation & Deployment
- ✅ `install/venv_setup.sh` - Added I2C packages
- ✅ `install/install_gui.sh` - Added i2c group configuration
- ✅ `gui/rpi_gui.service` - Added I2C group and dry-run env

### Documentation
- ✅ `README.md` - Updated to BME690
- ✨ `docs/BME690_SETUP.md` - NEW: Setup guide
- ✨ `docs/BME690_WIRING.md` - NEW: Wiring reference
- ✅ `DOCUMENTATION_INDEX.md` - Consolidated BME690 docs

---

## Deployment Workflow

### Development → Pi Deployment

```bash
# 1. On your development machine
cd ~/Code/GitHub/mrmagicbg/rpi-lab
git add .
git commit -m "feat: BME690 sensor migration"
git push origin main

# 2. On the Raspberry Pi (or via SSH)
sudo bash /opt/rpi-lab/deploy/quick_deploy.sh
# OR for full deployment:
sudo bash /opt/rpi-lab/deploy/deploy.sh

# 3. Verify deployment
sudo systemctl status rpi_gui.service
sudo journalctl -u rpi_gui.service -f
```

---

## Troubleshooting Guide

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Sensor not responding** | Reading shows "N/A" | Check I2C wiring and address (0x76/0x77) |
| **Permission denied** | Can't access I2C | `sudo usermod -a -G i2c mrmagic` (logout/login) |
| **Service won't start** | systemctl fails | Check logs: `sudo journalctl -u rpi_gui.service -n 50` |
| **Sensor not detected** | No device in i2cdetect | Run `sudo i2cdetect -y 1`, verify wiring and enable I2C |

---

## Common Commands

```bash
# Service management
sudo systemctl start rpi_gui.service
sudo systemctl stop rpi_gui.service
sudo systemctl restart rpi_gui.service
sudo systemctl enable rpi_gui.service
sudo systemctl status rpi_gui.service

# Testing and debugging
cd /opt/rpi-lab && source .venv/bin/activate && python3 -m sensors.bme690
sudo journalctl -u rpi_gui.service -f
sudo journalctl -u rpi_gui.service -n 50
sudo journalctl -u rpi_gui.service --since "1 hour ago"

# I2C verification
sudo i2cdetect -y 1  # Show I2C devices

# Permission management
sudo usermod -a -G i2c $USER
id $USER  # Verify group membership
```

---

## Documentation Links

- 📖 **Hardware & Setup**: See [docs/BME690_SETUP.md](docs/BME690_SETUP.md)
- 📖 **Wiring Reference**: See [docs/BME690_WIRING.md](docs/BME690_WIRING.md)
- 📚 **Project Overview**: See [README.md](README.md)

---

## Summary

The rpi-lab project now has:

✅ **Modern BME690 Support** - Well-maintained Pimoroni library  
✅ **Complete Documentation** - Wiring, setup, troubleshooting  
✅ **Automated Installation** - Simple setup scripts  
✅ **Production Ready** - Proper error handling and logging  
✅ **Easy Deployment** - GitHub-based workflow  
✅ **GUI Integration** - Real-time sensor display built-in  

**Status**: Ready for deployment and production use (hardware testing pending).

---

**Last Updated**: December 28, 2025  
**Repository**: https://github.com/mrmagicbg/rpi-lab  
**Maintainer**: mrmagicbg
# RPI Lab DHT22 Sensor - Complete Update Summary

**Date**: December 28, 2025  
**Status**: ✅ Ready for Deployment  
**Scope**: Full DHT22 sensor integration with modern library

---

## Overview

The rpi-lab project has been fully updated to support DHT22 temperature and humidity sensors with a modern, actively-maintained library stack. All components are now compatible with the latest Raspberry Pi OS versions (Bookworm, Trixie).

## What Changed

### 1. Core Sensor Implementation

**File**: `sensors/dht22.py`

**Changes**:
- ❌ Removed: Deprecated `Adafruit_DHT` library (platform compatibility issues)
- ✅ Added: `gpiozero==2.0.1` for modern GPIO control
- ✅ Added: Pure Python DHT22 protocol implementation with bit-level GPIO timing
- ✅ Added: Checksum validation for data integrity
- ✅ Added: Automatic retry logic for unreliable reads
- ✅ Maintained: Backward-compatible API (`read()`, `read_formatted()`)

**Features**:
- Works on modern Raspberry Pi OS (Bookworm, Trixie)
- No C/C++ compilation needed - fully available on piwheels
- Proper error handling and detailed logging
- Standalone testable (no GUI required)
- Custom DHT22 protocol decoder

### 2. Installation Scripts

**File**: `install/venv_setup.sh`

**Changes**:
- Simplified to use `requirements.txt` for all dependencies
- Removed hardcoded package list and special flags
- Added better error handling and progress indicators
- Now works with modern Python venv

**File**: `install/install_gui.sh`

**Changes**:
- Added automatic GPIO group configuration
- User `mrmagic` added to `gpio` group for hardware access
- Improved sudoers configuration (supports both GPIO and reboot)
- Better logging and error messages
- Updated documentation

### 3. Service Configuration

**File**: `gui/rpi_gui.service`

**Changes**:
- Added `SupplementaryGroups=gpio` for GPIO access without sudo
- Updated `WorkingDirectory` to `/opt/rpi-lab`
- Improved inline documentation
- Maintained backward compatibility

**Benefits**:
- GUI can read GPIO without root privileges
- Proper permissions management
- More secure deployment

### 4. Dependencies

**File**: `requirements.txt`

**Changes**:
```diff
- Adafruit-DHT==1.4.0  (deprecated, platform issues)
+ gpiozero==2.0.1      (modern, actively maintained)
```

**Result**:
- All packages installable on piwheels (no compilation)
- Faster installation (no build required)
- Better long-term support

### 5. Documentation (Updated)

**File**: `README.md`

**New DHT22 Section Includes**:
- Complete hardware wiring guide with GPIO pinout reference
- Step-by-step software installation
- Sensor testing procedures
- Configuration options (custom GPIO pins)
- Troubleshooting guide
- Sensor specifications and datasheet reference

### 6. Documentation (New Files)

**File**: `docs/DHT22_SETUP.md` (NEW)

**Comprehensive Guide Including**:
- Hardware requirements and specifications
- Detailed wiring diagrams (with/without pull-up)
- Physical Raspberry Pi pin layout reference
- Complete software installation steps
- Testing procedures with expected output
- Configuration for custom GPIO pins
- Technical protocol details
- Common issues and solutions
- Debugging commands and utilities
- References and datasheets

**File**: `DEPLOYMENT_CHECKLIST_DHT22.md` (NEW)

**Complete Verification Checklist**:
- Hardware setup verification
- Software installation steps
- Sensor testing procedures
- GUI integration testing
- Auto-start configuration
- Production readiness checklist
- Rollback procedures
- Maintenance schedule

**File**: `DHT22_INTEGRATION_SUMMARY.md` (NEW)

**Integration Overview Document**:
- Summary of all changes
- Quick start guide
- Hardware wiring reference
- File structure overview
- Testing checklist
- Deployment procedures
- Troubleshooting guide
- Key improvements made

**File**: `DHT22_QUICK_REFERENCE.md` (NEW)

**Quick Reference Card**:
- 30-second wiring guide
- 5-minute installation
- Common commands
- Quick troubleshooting
- GPIO pinout reference
- Next steps

---

## Installation Quick Start

### On Your Raspberry Pi

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-full python3-dev build-essential git

# 2. Clone and copy to /opt
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/

# 3. Run installation scripts
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/display_install.sh
sudo /opt/rpi-lab/install/install_gui.sh

# 4. Test sensor
cd /opt/rpi-lab
source .venv/bin/activate
python3 -m sensors.dht22

# 5. Reboot
sudo reboot
```

After reboot, GUI appears with live DHT22 readings.

---

## Hardware Wiring

```
DHT22 Module    Raspberry Pi GPIO
─────────────────────────────────
Pin 1 (VCC)  → Pin 1 (3.3V)
Pin 2 (DATA) → Pin 7 (GPIO4)
Pin 4 (GND)  → Pin 6 (GND)
Pin 3 (NULL) → Not connected

Optional: 4.7kΩ pull-up resistor
          Between Pin 1 (VCC) and Pin 7 (GPIO4)
```

---

## Testing & Verification

### Sensor Direct Test
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 -m sensors.dht22
```

**Expected Output**:
```
2025-12-28 16:56:36,408 - __main__ - INFO - DHT22 sensor initialized on GPIO4
Reading from DHT22 sensor on GPIO4...
Temperature: 23.5°C
Humidity: 45.2%
```

### GUI Verification
- [ ] GUI appears on boot automatically
- [ ] 🌡️ Temperature displayed in red (not N/A)
- [ ] 💧 Humidity displayed in cyan (not N/A)
- [ ] Status shows "✓ Last updated: HH:MM:SS" (green)
- [ ] Readings update every 5 seconds
- [ ] All 4 buttons responsive

---

## Key Improvements

| Improvement | Before | After |
|------------|--------|-------|
| **Library** | Adafruit_DHT (deprecated) | gpiozero (modern, maintained) |
| **Platform Support** | Limited to older Pi OS | Works on Bookworm, Trixie |
| **Installation** | Required compilation | Pure Python, instant install |
| **Availability** | Not on piwheels | Available on piwheels |
| **Error Handling** | Basic | Robust with checksum validation |
| **Documentation** | Minimal | Comprehensive with guides |
| **GPIO Access** | Required sudo | Automated group permissions |
| **Testing** | GUI only | Standalone sensor test available |

---

## Files Modified Summary

### Core Code
- ✅ `sensors/dht22.py` - Complete rewrite with modern implementation
- ✅ `requirements.txt` - Updated dependencies
- ✅ `gui/rpi_gui.py` - No changes (already properly integrated!)

### Installation & Deployment
- ✅ `install/venv_setup.sh` - Simplified and improved
- ✅ `install/install_gui.sh` - Added GPIO group configuration
- ✅ `gui/rpi_gui.service` - Added GPIO permissions

### Documentation
- ✅ `README.md` - Added comprehensive DHT22 section
- ✨ `docs/DHT22_SETUP.md` - NEW: Detailed hardware/software guide
- ✨ `DEPLOYMENT_CHECKLIST_DHT22.md` - NEW: Deployment verification
- ✨ `DHT22_INTEGRATION_SUMMARY.md` - NEW: Integration overview
- ✨ `DHT22_QUICK_REFERENCE.md` - NEW: Quick reference card

---

## Deployment Workflow

### Development → Pi Deployment

```bash
# 1. On your development machine
cd ~/Code/GitHub/mrmagicbg/rpi-lab
git add .
git commit -m "feat: DHT22 sensor improvements"
git push origin main

# 2. On the Raspberry Pi (or via SSH)
sudo bash /opt/rpi-lab/deploy/quick_deploy.sh
# OR for full deployment:
sudo bash /opt/rpi-lab/deploy/deploy.sh

# 3. Verify deployment
sudo systemctl status rpi_gui.service
sudo journalctl -u rpi_gui.service -f
```

---

## Troubleshooting Guide

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Sensor not responding** | Reading shows "N/A" | Check wiring: VCC=3.3V, GND=0V, GPIO4 connected |
| **Checksum errors** | Repeated read failures | Add 4.7kΩ pull-up resistor between VCC and DATA |
| **Permission denied** | Can't access GPIO | `sudo usermod -a -G gpio mrmagic` (logout/login) |
| **Service won't start** | systemctl fails | Check logs: `sudo journalctl -u rpi_gui.service -n 50` |
| **Sensor timeout** | Consistent timeouts | Move away from electrical interference, shorten wires |
| **Wrong readings** | Values seem incorrect | Verify sensor placement, check environmental conditions |

---

## Common Commands

```bash
# Service management
sudo systemctl start rpi_gui.service
sudo systemctl stop rpi_gui.service
sudo systemctl restart rpi_gui.service
sudo systemctl enable rpi_gui.service
sudo systemctl status rpi_gui.service

# Testing and debugging
cd /opt/rpi-lab && source .venv/bin/activate && python3 -m sensors.dht22
sudo journalctl -u rpi_gui.service -f
sudo journalctl -u rpi_gui.service -n 50
sudo journalctl -u rpi_gui.service --since "1 hour ago"

# GPIO verification
gpio -v  # Show GPIO info
gpio readall  # Show all GPIO states

# Permission management
sudo usermod -a -G gpio $USER
id $USER  # Verify group membership
```

---

## Documentation Links

- 📖 **Hardware & Setup**: See [docs/DHT22_SETUP.md](docs/DHT22_SETUP.md)
- ✅ **Deployment Checklist**: See [DEPLOYMENT_CHECKLIST_DHT22.md](DEPLOYMENT_CHECKLIST_DHT22.md)
- 📋 **Integration Summary**: See [DHT22_INTEGRATION_SUMMARY.md](DHT22_INTEGRATION_SUMMARY.md)
- ⚡ **Quick Reference**: See [DHT22_QUICK_REFERENCE.md](DHT22_QUICK_REFERENCE.md)
- 📚 **Project Overview**: See [README.md](README.md)

---

## Support & Next Steps

### For Initial Setup
1. Follow [DHT22_QUICK_REFERENCE.md](DHT22_QUICK_REFERENCE.md) (5 minutes)
2. Use [DEPLOYMENT_CHECKLIST_DHT22.md](DEPLOYMENT_CHECKLIST_DHT22.md) to verify

### For Detailed Help
1. See [docs/DHT22_SETUP.md](docs/DHT22_SETUP.md) for comprehensive guide
2. Check troubleshooting section above
3. Review service logs: `sudo journalctl -u rpi_gui.service -f`

### For Understanding Changes
- Read [DHT22_INTEGRATION_SUMMARY.md](DHT22_INTEGRATION_SUMMARY.md)
- Review modified files (noted above)

---

## Summary

The rpi-lab project now has:

✅ **Modern DHT22 Support** - Using active, well-maintained libraries  
✅ **Complete Documentation** - Guides, checklists, and troubleshooting  
✅ **Automated Installation** - Simple setup scripts  
✅ **Production Ready** - Proper error handling and logging  
✅ **Easy Deployment** - GitHub-based workflow  
✅ **GUI Integration** - Real-time sensor display built-in  

**Status**: Ready for deployment and production use.

---

**Last Updated**: December 28, 2025  
**Repository**: https://github.com/mrmagicbg/rpi-lab  
**Maintainer**: mrmagicbg
