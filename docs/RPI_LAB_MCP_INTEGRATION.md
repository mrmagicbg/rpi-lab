# RPI Lab & MCP Server Integration Guide

## Overview

The RPI Lab project is now fully integrated with the MCP Server for remote sensor monitoring and control. This guide documents the integration, prerequisites, and deployment procedures.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  RPi Lab GUI (tkinter)                                          │
│  ├─ BME690 Sensor (I2C, 0x76/0x77)                            │
│  ├─ Display: Temp, Humidity, Pressure, Gas Resistance        │
│  └─ Local systemd service (auto-start)                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                  I2C + GPIO
                       │
┌──────────────────────┴──────────────────────────────────────────┐
│  Raspberry Pi                                                   │
│  ├─ Python 3.12                                               │
│  ├─ Virtual Environment (.venv)                               │
│  ├─ GPIO & I2C kernel modules                                 │
│  └─ systemd services (rpi_gui.service)                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                 SSH / HTTP
                       │
┌──────────────────────┴──────────────────────────────────────────┐
│  MCP Server (remote monitoring)                                │
│  ├─ Port 3030: FastAPI HTTP API                               │
│  ├─ Port 5000: Spec-Kit Web UI                                │
│  ├─ BME690 MCP Tools (/api/bme690/*)                         │
│  └─ Sensor data available to AI agents                        │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Hardware
- Raspberry Pi 4, Pi 5, or Pi Zero 2 (with GPIO header)
- BME690 environmental sensor breakout (Pimoroni recommended)
- I2C wiring: SDA (GPIO 2), SCL (GPIO 3), VIN (3.3V), GND
- Display: Waveshare 4.3" DSI or equivalent

### Software
- Raspberry Pi OS (Bookworm or Trixie)
- Python 3.11+
- Git
- build-essential, i2c-tools
- Virtual environment support

### Network (for MCP integration)
- SSH access to MCP server (10.10.10.24)
- HTTP connectivity on ports 3030 (API) and 5000 (Web UI)

## Installation Steps

### Step 1: Prepare Raspberry Pi

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Enable I2C interface
sudo raspi-config nonint do_i2c 0

# Verify I2C enabled
i2cdetect -y 1
# Should show device at 0x76 or 0x77
```

### Step 2: Clone RPI Lab Repository

```bash
cd /opt
sudo git clone https://github.com/mrmagicbg/rpi-lab.git
cd rpi-lab
```

### Step 3: Run Installation Scripts

```bash
# Phase 1: Virtual environment setup with prerequisite checking
sudo bash install/venv_setup.sh

# Phase 2: GUI installation with I2C verification
sudo bash install/install_gui.sh

# Verify venv
source .venv/bin/activate
python3 -c "import bme690; print('✓ BME690 available')"
```

### Step 4: Verify BME690 Sensor

```bash
# Test sensor directly
.venv/bin/python3 sensors/bme690.py

# Check I2C connection
i2cdetect -y 1

# View sensor status
journalctl -u rpi_gui.service -n 20
```

## MCP Server Integration

### Exposing Sensor Data to MCP

The RPI Lab project includes an MCP tool module for remote sensor access:

```python
from sensors.bme690_mcp import BME690MCPTools

tools = BME690MCPTools()

# Get all readings
print(tools.read_all())

# Get specific measurements
print(tools.read_temperature())
print(tools.read_humidity())
print(tools.read_pressure())
print(tools.read_gas_resistance())
```

### HTTP Endpoints via MCP Server

Once integrated, the MCP server exposes:

```
GET http://10.10.10.24:3030/api/sensors/bme690/all
GET http://10.10.10.24:3030/api/sensors/bme690/temperature
GET http://10.10.10.24:3030/api/sensors/bme690/humidity
GET http://10.10.10.24:3030/api/sensors/bme690/pressure
GET http://10.10.10.24:3030/api/sensors/bme690/gas
```

### Testing from MCP Server

```bash
# Using the MCP CLI
python3 mcp_cmd.py "python3 /opt/rpi-lab/sensors/bme690_mcp.py"

# Direct HTTP test
curl http://10.10.10.24:3030/api/sensors/bme690/all | jq .
```

## Deployment Checklist

### Local RPI Lab Deployment

- [ ] Raspberry Pi OS installed (Bookworm/Trixie)
- [ ] I2C enabled and BME690 detected (0x76 or 0x77)
- [ ] venv_setup.sh completed successfully
- [ ] install_gui.sh completed with no errors
- [ ] GUI service active: `systemctl status rpi_gui.service`
- [ ] Sensor readings display correctly on GUI
- [ ] `sensors/bme690.py` test runs without errors

### MCP Server Integration

- [ ] rpi-lab/.venv/bin/python3 works
- [ ] `sensors/bme690_mcp.py` test runs successfully
- [ ] MCP server has SSH access to Pi
- [ ] Firewall allows ports 3030, 5000 from Pi
- [ ] HTTP endpoints respond correctly
- [ ] MCP /commands list includes bme690_mcp.py reference

## Configuration

### GUI Configuration

Edit `gui/rpi_gui.py`:
- Sensor update interval (default 5 seconds)
- I2C address (0x76 or 0x77)
- Display colors and fonts
- Button actions

### Sensor Configuration

Edit `sensors/bme690.py`:
- Oversampling settings (temperature, humidity, pressure)
- Gas heater temperature (default 320°C)
- Gas heater duration (default 150 ms)
- Dry-run mode: `BME690_DRY_RUN=1`

### Service Configuration

Edit `/etc/systemd/system/rpi_gui.service`:
- User running service (default: mrpi)
- Display settings
- Environment variables
- Auto-restart behavior

## Troubleshooting

### "I2C device not found"
```bash
# Check wiring
i2cdetect -y 1

# Enable I2C if needed
sudo raspi-config nonint do_i2c 0

# Verify pull-up resistors on breakout board (typically 2.2kΩ)
```

### "BME690 library not found"
```bash
# Reinstall from venv
source .venv/bin/activate
pip install bme690==0.3.2
```

### "Permission denied" for I2C
```bash
# Add user to i2c group
sudo usermod -aG i2c $USER

# Reload groups
newgrp i2c

# Or restart system
sudo reboot
```

### GUI doesn't start
```bash
# Check logs
journalctl -u rpi_gui.service -f

# Test manually
/opt/rpi-lab/.venv/bin/python3 /opt/rpi-lab/gui/rpi_gui.py

# Check X11 display
echo $DISPLAY

# Verify tkinter
.venv/bin/python3 -c "import tkinter; print('OK')"
```

### Sensor readings "N/A"
- Verify I2C connection: `i2cdetect -y 1`
- Check wiring (VIN, GND, SDA, SCL)
- Gas heater stability: may take 5-10 readings to stabilize
- Enable debug logging in `sensors/bme690.py`

## Vendor Documentation Reference

See [docs/BME690_VENDOR_RESOURCES.md](docs/BME690_VENDOR_RESOURCES.md) for:
- Official Bosch datasheets
- Pimoroni library documentation
- Hardware specifications
- Application notes and examples

## Files Modified/Added (Pass 1 & 2)

### Installation Scripts
- `install/venv_setup.sh` - Enhanced with prerequisite checking
- `install/install_gui.sh` - Added I2C verification and user groups

### Sensor Modules
- `sensors/bme690.py` - Enhanced error handling (existing)
- `sensors/bme690_mcp.py` - New MCP tool integration
- `sensors/__init__.py` - Package initialization

### Documentation
- `docs/BME690_VENDOR_RESOURCES.md` - New vendor resources guide
- `docs/RPI_LAB_MCP_INTEGRATION.md` - New integration guide (this file)

### GUI
- `gui/rpi_gui.py` - Already displays all BME690 data (temperature, humidity, pressure, gas)

## Next Steps

1. **Deploy to Raspberry Pi:**
   ```bash
   sudo bash install/venv_setup.sh
   sudo bash install/install_gui.sh
   ```

2. **Verify Local Operation:**
   ```bash
   systemctl status rpi_gui.service
   journalctl -u rpi_gui.service -f
   ```

3. **Test MCP Integration:**
   ```bash
   .venv/bin/python3 sensors/bme690_mcp.py
   ```

4. **Monitor Remotely:**
   - Access GUI on Pi display
   - Query via MCP HTTP API
   - Log sensor data for analysis

## Support

For issues or questions:
1. Check [docs/BME690_VENDOR_RESOURCES.md](docs/BME690_VENDOR_RESOURCES.md) for vendor support
2. Review logs: `journalctl -u rpi_gui.service`
3. Run manual sensor test: `sensors/bme690.py`
4. Test I2C: `i2cdetect -y 1`

---

**Last Updated:** December 28, 2025  
**Version:** 1.0  
**For RPI Lab + MCP Server Integration**
