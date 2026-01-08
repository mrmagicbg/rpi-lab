# BME690 & Speaker Wiring Guide

## Hardware Overview

This guide covers the wiring for:
- **BME690 Environmental Sensor** (I2C) - Temperature, humidity, pressure, and gas
- **PWM Speaker** (GPIO 12) - Audio alerts for sensor thresholds

---

## BME690 Environmental Sensor Wiring

### Pin Connections (Raspberry Pi 3/4)

| BME690 Pin | Raspberry Pi Pin | Description |
|------------|------------------|-------------|
| **VCC** | Pin 1 (3.3V) | Power supply (3.3V recommended) |
| **GND** | Pin 6 (GND) | Ground |
| **SDA** | Pin 3 (GPIO2 / SDA1) | I2C Data line |
| **SCL** | Pin 5 (GPIO3 / SCL1) | I2C Clock line |

### I2C Address Configuration

- **Default address**: `0x76` (ADDR trace uncut)
- **Alternate address**: `0x77` (cut ADDR trace on breakout for second sensor)

### Qwiic / STEMMA QT Connector

The BME690 breakout includes a Qwiic/STEMMA QT connector for plug-and-play wiring with compatible cables and HATs. This connector provides:
- Reverse polarity protection
- Standardized 4-pin JST connector
- Easy daisy-chaining of multiple I2C devices

### Verification Steps

1. **Enable I2C on Raspberry Pi**:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   ```

2. **Reboot**:
   ```bash
   sudo reboot
   ```

3. **Scan I2C bus** to verify sensor detection:
   ```bash
   i2cdetect -y 1
   ```
   
   Expected output showing sensor at address `76`:
   ```
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
   00:                         -- -- -- -- -- -- -- -- 
   10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
   20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
   30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
   40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
   50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
   60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
   70: -- -- -- -- -- -- 76 --
   ```

4. **Test the sensor**:
   ```bash
   cd /opt/rpi-lab
   source .venv/bin/activate
   python3 sensors/bme690.py
   ```

---

## PWM Speaker Wiring

### Pin Connections

| Speaker Wire | Raspberry Pi Pin | Description |
|--------------|------------------|-------------|
| **Red (+)** | Pin 32 (GPIO12) | PWM output (hardware PWM channel 0) |
| **Black (-)** | Pin 6 or 9 (GND) | Ground |

### GPIO Pin Details

- **GPIO12** (physical pin 32) supports **hardware PWM channel 0**
- Hardware PWM provides clean, consistent audio tones without software jitter
- Default frequency: **2000 Hz** (pleasant beep tone)
- Duty cycle: **50%** (square wave)

### Speaker Specifications

- **Impedance**: 8Ω typical (most small piezo or dynamic speakers)
- **Power**: Low power (GPIO can drive small speakers directly)
- **Volume**: Controlled by PWM duty cycle (software adjustable)

### Alert Patterns

The speaker provides audio feedback for:

| Event | Pattern | Frequency |
|-------|---------|-----------|
| **Gas Alert** | Double beep | Every 15 seconds when volatile gases detected |
| **Temperature Alert** | Triple beep | Hourly when < 0°C or > 30°C |
| **Humidity Alert** | Double beep | Hourly when < 25% or > 80% |
| **Startup** | Long beep | On GUI launch |
| **Shutdown** | Long beep | On GUI exit |
| **Reboot** | Triple beep | Before system reboot |
| **Test** | Special pattern | Via "Test Speaker" button |

### Verification Steps

1. **Test the speaker module**:
   ```bash
   cd /opt/rpi-lab
   source .venv/bin/activate
   python3 sensors/speaker.py
   ```

2. **Test via GUI**: Launch the GUI and press the "🔊 Test Speaker" button.

---

## Complete Wiring Diagram

```
Raspberry Pi (Physical Pin Layout)
=====================================
       3.3V [ 1]  [ 2] 5V
  I2C SDA2 [ 3]  [ 4] 5V
  I2C SCL3 [ 5]  [ 6] GND  ←─┐
              ...              │
                               │
             [32]  [33]        │
         GPIO12    GPIO13      │
           ↓                   │
        Speaker+             Speaker-
        (Red)               (Black)
        
BME690 Sensor Connections:
  - VCC → Pin 1 (3.3V)
  - GND → Pin 6 (GND)
  - SDA → Pin 3 (GPIO2)
  - SCL → Pin 5 (GPIO3)
```

---

## Troubleshooting

### BME690 Sensor Issues

**Problem**: Sensor not detected (`i2cdetect` shows no device at 0x76)

**Solutions**:
1. Verify I2C is enabled: `sudo raspi-config` → Interface Options → I2C
2. Check wiring connections (especially SDA/SCL)
3. Ensure 3.3V power is connected
4. Try alternate I2C address 0x77 (cut ADDR trace)
5. Check for I2C bus errors: `dmesg | grep i2c`

**Problem**: Sensor readings show "N/A"

**Solutions**:
1. Sensor may be warming up (gas heater takes ~5 minutes to stabilize)
2. Check I2C bus health: `i2cget -y 1 0x76 0xd0` (should return chip ID 0x61)
3. Review logs: `journalctl -u rpi_gui.service -n 50`

### Speaker Issues

**Problem**: No sound from speaker

**Solutions**:
1. Verify GPIO12 is not used by another service
2. Check speaker wiring (red to pin 32, black to GND)
3. Test speaker module directly: `python3 sensors/speaker.py`
4. Ensure speaker is not damaged (test with multimeter for continuity)
5. Increase PWM duty cycle in code if volume too low

**Problem**: Distorted or buzzing sound

**Solutions**:
1. Check for loose connections
2. Ensure proper grounding
3. Try different speaker (impedance mismatch)
4. Adjust PWM frequency (default 2000 Hz, try 1000-3000 Hz range)

---

## Additional Notes

### Hardware PWM vs Software PWM

GPIO12 is one of the few pins on Raspberry Pi with **hardware PWM** support:
- **Hardware PWM**: Dedicated hardware generates precise timing (better audio quality)
- **Software PWM**: CPU-driven timing (can have jitter, especially under load)

Using GPIO12 ensures clean, consistent beep tones without affecting system performance.

### Multiple Sensors

To add a second BME690 sensor:
1. Cut the ADDR trace on the second breakout to change address to 0x77
2. Connect both sensors to the same I2C bus (SDA/SCL lines)
3. Modify code to initialize: `sensor2 = BME690Sensor(i2c_addr=0x77)`

### Power Considerations

- BME690 draws ~3.7 mA average (12 mA peak during gas measurement)
- Speaker draws minimal current from GPIO (< 20 mA)
- Total system power < 100 mA (well within Pi's capabilities)
- External power supply not required for these peripherals

---

## Safety Notes

⚠️ **Important Safety Information**:

1. **Never connect 5V to BME690 VCC** - Use 3.3V only to prevent damage
2. **Do not exceed GPIO pin ratings** - Maximum 16 mA per pin, 50 mA total
3. **Verify polarity** before connecting speaker (red to GPIO, black to GND)
4. **Disconnect power** before making wiring changes
5. **Use proper wire gauge** - 22-26 AWG solid core recommended for breadboard

---

## Quick Reference

### One-Line Wiring Summary

**BME690**: VCC→Pin1(3.3V), GND→Pin6, SDA→Pin3(GPIO2), SCL→Pin5(GPIO3)  
**Speaker**: Red→Pin32(GPIO12), Black→Pin6(GND)

### Quick Test Commands

```bash
# Test I2C bus
i2cdetect -y 1

# Test BME690 sensor
cd /opt/rpi-lab && source .venv/bin/activate && python3 sensors/bme690.py

# Test speaker
cd /opt/rpi-lab && source .venv/bin/activate && python3 sensors/speaker.py

# View GUI logs
journalctl -u rpi_gui.service -f
```

---

**Document Version**: 3.0.0  
**Last Updated**: January 8, 2026  
**Hardware Tested**: Raspberry Pi 3 Model B, Pimoroni BME690 Breakout, Generic 8Ω Speaker
