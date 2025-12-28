# BME690 Environmental Sensor - Vendor Resources & Documentation

## Overview

The **BME690** is a state-of-the-art environmental sensor manufactured by **Bosch Sensortec** that combines temperature, humidity, pressure, and gas resistance measurements in a single I2C device. This document provides direct links to vendor resources and integration details.

## Official Vendor Documentation

### Bosch Sensortec (Official Manufacturer)

**Sensor Datasheet:**
- **Download:** https://www.bosch-sensortec.com/media/boschsensortec_content/dam/sensortech/systempages/Common/Bosch_Sensortec_BME690_Datasheet.pdf
- **Key Specs:**
  - Temperature Range: -40 to +85 °C
  - Humidity Range: 0 to 100 %RH
  - Pressure Range: 300 to 1100 hPa
  - Gas Resistance: Highly sensitive to reducing gases
  - I2C Addresses: Primary 0x76, Secondary 0x77
  - Supply Voltage: 1.7 to 3.6 V

**Application Notes:**
- https://www.bosch-sensortec.com/media/boschsensortec_content/dam/sensortech/systempages/Common/bst-bme690-AN000-10-1.pdf
- Includes detailed calibration procedures and typical applications

**Community Resources:**
- GitHub: https://github.com/BoschSensortec/BME680_driver (reference driver)
- Technical Support: https://community.bosch-sensortec.com/

### Pimoroni Breakout Board

If using Pimoroni's BME690 breakout (recommended for Raspberry Pi):

**Product Page:**
- https://shop.pimoroni.com/products/bme690-breakout
- Schematic, pinout, and wiring diagrams
- Troubleshooting guides

**Pimoroni Python Library:**
- **GitHub:** https://github.com/pimoroni/bme690-python
- **PyPI:** https://pypi.org/project/bme690/
- Current version: 0.3.2
- Pure Python implementation (no C dependencies)
- Supports Raspberry Pi OS Bookworm and Trixie

**Installation:**
```bash
pip install bme690==0.3.2
```

**Library Features:**
- Auto-detection of I2C address (0x76 or 0x77)
- Configurable oversampling for all measurements
- Gas heater temperature/duration control
- Multiple sensor profiles

## Raspberry Pi Integration

### Hardware Requirements

1. **Raspberry Pi** (tested on Pi 4, Pi Zero 2, Pi 5)
2. **BME690 Breakout Board** (Pimoroni recommended)
3. **I2C Wiring:**
   ```
   BME690 Breakout → Raspberry Pi GPIO
   VIN (3.3V)      → Pin 1 (3.3V)
   GND             → Pin 6 (GND)
   SDA (GPIO 2)    → Pin 3 (SDA)
   SCL (GPIO 3)    → Pin 5 (SCL)
   ```

### I2C Configuration

**Enable I2C Interface:**
```bash
sudo raspi-config
# Navigate: 3 Interface Options → I2C → Enable
```

**Verify I2C Availability:**
```bash
i2cdetect -y 1
# Should show device at 0x76 or 0x77
```

**Check Kernel Modules:**
```bash
lsmod | grep i2c
# Output should show: i2c_bcm2835, i2c_dev
```

## Data Output & Specifications

### Temperature (°C)
- **Range:** -40 to +85 °C
- **Accuracy:** ±1 °C (typical)
- **Resolution:** 0.01 °C
- **Use Case:** Environmental monitoring, comfort assessment

### Humidity (%RH)
- **Range:** 0 to 100 %
- **Accuracy:** ±3 % (typical)
- **Resolution:** 0.1 %
- **Use Case:** Moisture detection, comfort index

### Pressure (hPa)
- **Range:** 300 to 1100 hPa
- **Accuracy:** ±1 hPa (typical)
- **Resolution:** 0.01 hPa
- **Use Case:** Altitude calculation, weather prediction, barometric pressure
- **Relationship:** `Altitude (m) = 44330 * (1.0 - (P/P0)^(1/5.255))`

### Gas Resistance (Ohms)
- **Range:** 100 Ω to 10 MΩ
- **Sensitivity:** Reduces with presence of reducing gases (ethanol, VOCs, CO)
- **Use Cases:**
  - Air quality assessment
  - Gas/vapor detection
  - Indoor air quality (IAQ) index
  - Breath detection (with pattern recognition)

**Heating Profile:**
- Temperature: 320 °C
- Duration: 150 ms
- Stabilizes gas sensor response

**Gas Index Calculation (IAQ):**
Bosch provides algorithms to convert raw resistance to IAQ (0-500 scale)
- See: https://github.com/pimoroni/bme690-python/blob/master/examples/gas.py

## Integration with RPI Lab GUI

### Display Configuration

The RPI Lab GUI displays all four sensor measurements:

```python
# Temperature (°C) - Red indicator
# Humidity (%) - Cyan indicator
# Pressure (hPa) - Yellow indicator
# Gas Resistance (Ohms) - Purple indicator
```

### Data Refresh Rate

- **Default:** 5 seconds
- **Configuration:** Editable in `gui/rpi_gui.py`
- **Heating Profile:** ~150 ms per reading

### Error Handling

- **Sensor Unavailable:** Shows "—" with warning icon
- **I2C Error:** Logs to console; GUI continues with last valid reading
- **Dry-Run Mode:** Set `BME690_DRY_RUN=1` for testing without hardware

## Vendor-Provided Examples & Tools

### Official Pimoroni Examples

**Location:** https://github.com/pimoroni/bme690-python/tree/master/examples

1. **gas.py** - Gas sensor with IAQ algorithm
2. **gas-fast.py** - Rapid gas measurements
3. **sensor.py** - Basic temperature/humidity/pressure
4. **altitude.py** - Altitude calculation from pressure

### Bosch Reference Driver

**Location:** https://github.com/BoschSensortec/BME690_driver/blob/master/examples/

C examples for bare-metal integration (advanced users)

## Troubleshooting Resources

### Pimoroni Support
- **Troubleshooting:** https://shop.pimoroni.com/products/bme690-breakout#tech-specs
- **Forum:** https://forums.pimoroni.com/

### Bosch Community
- **Technical Support:** https://community.bosch-sensortec.com/t5/Sensors/ct-p/sensortech
- **FAQs:** https://community.bosch-sensortec.com/t5/Sensors/tkb-p/sensor-knowledge-base

### Common Issues

**Issue:** I2C device not found (0x76 or 0x77)
- Check wiring (SDA, SCL, VIN, GND)
- Verify pull-up resistors (typically 2.2kΩ on breakout board)
- Test with `i2cdetect -y 1`

**Issue:** Gas readings unstable or always 0
- Ensure heater has warmed up (5-10 readings)
- Reduce measurement interval or increase heater temperature

**Issue:** Temperature offset or incorrect readings
- Verify calibration with Pimoroni library
- Check for I2C communication errors

## Summary Table

| Specification | Detail |
|---|---|
| **Manufacturer** | Bosch Sensortec |
| **Part Number** | BME690 |
| **Interface** | I2C (400 kHz standard, 1 MHz fast) |
| **I2C Address** | 0x76 (primary) or 0x77 (secondary) |
| **Supply Voltage** | 1.7 - 3.6 V (3.3V typical on Pi) |
| **Current (Idle)** | ~0.1 mA |
| **Current (Active)** | ~12 mA (with gas heater) |
| **Package** | LGA (Land Grid Array) 8-pin |
| **Breakout Vendor** | Pimoroni (recommended) |
| **Python Library** | bme690==0.3.2 (Pimoroni) |
| **Last Updated** | December 2025 |

## References

- **Bosch Sensortec Official Site:** https://www.bosch-sensortec.com/
- **Pimoroni GitHub:** https://github.com/pimoroni/bme690-python
- **RPI Lab Project:** Integration guide in this repository
- **Raspberry Pi GPIO Pinout:** https://pinout.xyz/

---

**Document Version:** 1.0  
**Created:** December 28, 2025  
**For Use With:** RPI Lab GUI & MCP Server Integration
