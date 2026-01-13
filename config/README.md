# RPI Lab Configuration

This directory contains configuration files for the RPI Lab sensor system.

## sensor.conf

Main sensor configuration file for BME690 environmental sensor.

### Location Priority

The system searches for config files in this order:
1. `/opt/rpi-lab/config/sensor.conf` (production)
2. `<repo>/config/sensor.conf` (development)
3. `~/.config/rpi-lab/sensor.conf` (user override)

### Quick Calibration Guide

**Problem: Humidity reads too low (e.g., 38% vs reference 74%)**

1. Try disabling gas heater first:
   ```ini
   enable_gas = no
   ```

2. If still off, add offset:
   ```ini
   enable_gas = no
   humidity_offset = 36.0  # (74 - 38 = 36)
   ```

3. Restart services:
   ```bash
   sudo systemctl restart rpi_gui.service
   sudo systemctl restart mqtt_publisher.service
   ```

**Salt Test Calibration (recommended)**

1. Prepare saturated salt solution (75% RH reference at 25°C)
2. Place sensor and reference meter in sealed container
3. Wait 8-12 hours for equilibrium
4. Read both values
5. Calculate offset: `offset = 75 - bme690_reading`
6. Update `sensor.conf` and restart

### Configuration Options

See comments in `sensor.conf` for detailed parameter descriptions.

### Verification

Check logs for calibration status:
```bash
sudo journalctl -u mqtt_publisher.service | grep calibration
python3 gui/rpi_gui.py  # Look for orange calibration status line
```

### Backup

Before major changes:
```bash
cp /opt/rpi-lab/config/sensor.conf /opt/rpi-lab/config/sensor.conf.backup
```
