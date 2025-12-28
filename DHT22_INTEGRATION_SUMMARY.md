# RPI Lab DHT22 Sensor Integration - Summary

## What's Been Updated

This document summarizes all updates made to the rpi-lab project to fully integrate the DHT22 sensor with the GUI application.

### 1. Core Sensor Module (`sensors/dht22.py`)

**Changes:**
- Replaced deprecated `Adafruit_DHT` with pure Python implementation using `gpiozero` and `RPi.GPIO`
- Implemented custom DHT22 protocol decoder (bit-level GPIO timing)
- Added automatic checksum validation
- Added retry logic for unreliable reads
- Maintained backward-compatible API (`read()`, `read_formatted()`)

**Features:**
- Works on modern Raspberry Pi OS (Bookworm, Trixie)
- Available on piwheels (no compilation needed)
- Proper error handling and logging
- Testable without GUI

### 2. GUI Application (`gui/rpi_gui.py`)

**No changes needed** - Already properly integrated!

**Current Features:**
- Real-time DHT22 temperature and humidity display
- Auto-updates every 5 seconds
- Connection status indication
- Error handling with user-friendly messages
- Persistent sensor display (always visible, no popup needed)

### 3. Installation Scripts

#### `install/venv_setup.sh`
- Updated to use `requirements.txt` for all dependencies
- Simplified installation process
- Added proper error handling

#### `install/install_gui.sh`
- Added GPIO group configuration
- Added user to `gpio` group automatically
- Improved sudoers configuration for passwordless operations
- Better error messages and logging

### 4. Service Configuration (`gui/rpi_gui.service`)

**Changes:**
- Added `SupplementaryGroups=gpio` for GPIO access without sudo
- Updated working directory to `/opt/rpi-lab`
- Improved documentation with setup instructions
- Maintained backward compatibility

### 5. Requirements File (`requirements.txt`)

**Changes:**
- Removed `Adafruit-DHT` (platform compatibility issues)
- Added `gpiozero==2.0.1` (modern, actively maintained)
- Simplified dependencies (now fully installable on piwheels)

### 6. Documentation

#### Updated `README.md`
- Complete DHT22 sensor setup guide
- Wiring diagram with GPIO pin references
- Testing instructions
- Troubleshooting section
- Configuration options for custom GPIO pins
- Sensor specifications and datasheet reference

#### New `docs/DHT22_SETUP.md`
- Comprehensive hardware wiring guide
- Detailed installation instructions
- Troubleshooting procedures with solutions
- Technical specifications
- Debugging commands
- Common issues and resolutions

#### New `DEPLOYMENT_CHECKLIST_DHT22.md`
- Step-by-step deployment verification
- Hardware setup verification
- Software installation checklist
- Testing procedures
- Auto-start configuration
- Production readiness checklist

## Quick Start

### On Your Raspberry Pi

1. **Install dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-full python3-dev build-essential git
   ```

2. **Clone and setup:**
   ```bash
   git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
   sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
   ```

3. **Run installation scripts:**
   ```bash
   sudo /opt/rpi-lab/install/venv_setup.sh
   sudo /opt/rpi-lab/install/display_install.sh
   sudo /opt/rpi-lab/install/install_gui.sh
   ```

4. **Test sensor:**
   ```bash
   cd /opt/rpi-lab
   source .venv/bin/activate
   python3 -m sensors.dht22
   ```

5. **Reboot:**
   ```bash
   sudo reboot
   ```

After reboot, the GUI should appear with live DHT22 readings.

## Hardware Wiring

```
DHT22 Module    →    Raspberry Pi
────────────────────────────────
VCC (Pin 1)     →    Pin 1 (3.3V)
DATA (Pin 2)    →    Pin 7 (GPIO4)
GND (Pin 4)     →    Pin 6 (GND)
NULL (Pin 3)    →    Not connected
```

Optional: Add 4.7kΩ pull-up resistor between VCC and DATA pins if sensor is unreliable.

## File Structure

```
rpi-lab/
├── sensors/
│   └── dht22.py          ← Updated sensor module
├── gui/
│   ├── rpi_gui.py        ← Already integrated (no changes)
│   └── rpi_gui.service   ← Updated service file
├── install/
│   ├── venv_setup.sh     ← Updated
│   └── install_gui.sh    ← Updated
├── docs/
│   └── DHT22_SETUP.md    ← NEW comprehensive guide
├── requirements.txt       ← Updated
├── README.md             ← Updated with full DHT22 section
└── DEPLOYMENT_CHECKLIST_DHT22.md  ← NEW checklist
```

## Testing Checklist

### Before GUI Auto-start

```bash
# 1. Activate venv
cd /opt/rpi-lab
source .venv/bin/activate

# 2. Test sensor directly
python3 -m sensors.dht22

# Expected output:
# Temperature: XX.X°C
# Humidity: YY.Y%
```

### After GUI Auto-start

- [ ] GUI appears on boot (no manual intervention)
- [ ] Temperature display shows reasonable value (not N/A)
- [ ] Humidity display shows reasonable value (not N/A)
- [ ] Status shows "✓ Last updated: HH:MM:SS" (green)
- [ ] Readings update every 5 seconds
- [ ] All 4 buttons are responsive

## Deployment

### For Development

```bash
# Make code changes
cd ~/Code/GitHub/mrmagicbg/rpi-lab
vim gui/rpi_gui.py

# Test locally
python3 -m py_compile gui/rpi_gui.py

# Push to GitHub
git add .
git commit -m "feat: DHT22 sensor improvements"
git push origin main

# Deploy to Pi
ssh pi "sudo bash /opt/rpi-lab/deploy/quick_deploy.sh"
```

### For Fresh Installation

Use the deployment checklist: `DEPLOYMENT_CHECKLIST_DHT22.md`

## Troubleshooting

### Sensor shows "N/A"

1. Check wiring:
   ```bash
   # Verify 3.3V on pin 1
   # Verify 0V on pin 6
   ```

2. Check GPIO access:
   ```bash
   sudo usermod -a -G gpio mrmagic
   # Log out and back in
   ```

3. Add pull-up resistor (4.7kΩ between VCC and DATA)

4. Check logs:
   ```bash
   sudo journalctl -u rpi_gui.service -f
   ```

### Service won't start

```bash
# Check service logs
sudo journalctl -u rpi_gui.service -n 50

# Verify virtualenv exists
ls -la /opt/rpi-lab/.venv/bin/python

# Check display is running
ps aux | grep Xorg
```

### Checksum errors in logs

This typically means electrical noise. Solutions:

1. Shorten sensor wires (< 1 meter)
2. Add 4.7kΩ pull-up resistor
3. Move sensor away from RF sources (WiFi, RF modules)
4. Use shielded cable if available

## Key Improvements

✅ **Modern Library** - Uses actively maintained `gpiozero` instead of deprecated Adafruit library

✅ **Better Compatibility** - Works on latest Raspberry Pi OS versions (Bookworm, Trixie)

✅ **Easier Installation** - No compilation needed, available on piwheels

✅ **Robust Protocol** - Custom DHT22 implementation with checksum validation

✅ **Better Documentation** - Comprehensive guides, wiring diagrams, troubleshooting

✅ **Production Ready** - Proper error handling, logging, and deployment scripts

✅ **Automated Testing** - Easy sensor verification before GUI startup

## Support & Debugging

### Useful Commands

```bash
# Test sensor
cd /opt/rpi-lab && source .venv/bin/activate && python3 -m sensors.dht22

# Check service status
sudo systemctl status rpi_gui.service

# View service logs (live)
sudo journalctl -u rpi_gui.service -f

# Check if GPIO is working
gpio -v

# Add user to gpio group
sudo usermod -a -G gpio $(whoami)

# Verify installation
python3 -c "import gpiozero; print('gpiozero OK')"
python3 -c "import RPi.GPIO; print('RPi.GPIO OK')"
```

### Logs Location

- **GUI Service Logs**: `sudo journalctl -u rpi_gui.service`
- **TPMS Session Logs**: `~/rpi-lab/logs/tpms/`
- **System Logs**: `/var/log/syslog`

## References

- [DHT22 Datasheet](https://www.rototron.info/dht22-tutorial-for-raspberry-pi/)
- [gpiozero Documentation](https://gpiozero.readthedocs.io/)
- [RPi.GPIO Documentation](https://pypi.org/project/RPi.GPIO/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)

---

**Last Updated:** December 28, 2025  
**Project Repository:** https://github.com/mrmagicbg/rpi-lab
