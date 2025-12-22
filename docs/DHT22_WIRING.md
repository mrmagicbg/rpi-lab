# DHT22 Temperature & Humidity Sensor - Wiring Guide

## Overview

The DHT22 (also known as AM2302) is a digital temperature and humidity sensor with the following specifications:

- **Temperature Range**: -40°C to 80°C (±0.5°C accuracy)
- **Humidity Range**: 0-100% RH (±2-5% accuracy)
- **Operating Voltage**: 3.3V - 5V
- **Interface**: Single-wire digital (1-Wire protocol)
- **Sampling Rate**: 0.5 Hz (readings every 2 seconds)

## Pin Configuration

DHT22 has 4 pins (left to right when facing the front with perforated side):

```
┌─────────────┐
│  DHT22      │
│  AM2302     │
│             │
│ ░░░░░░░░░░░ │ ← Perforated/mesh side
│             │
└─┬─┬─┬─┬─────┘
  1 2 3 4

Pin 1: VCC (3.3V - 5V)
Pin 2: DATA (signal)
Pin 3: NULL (not connected)
Pin 4: GND (ground)
```

## Wiring Diagram - Raspberry Pi to DHT22

### Connection Table

| DHT22 Pin | Wire Color | Raspberry Pi Pin | GPIO # | Description |
|-----------|------------|------------------|--------|-------------|
| Pin 1 (VCC) | Red | Pin 1 | 3.3V | Power supply |
| Pin 2 (DATA) | Yellow/White | Pin 7 | GPIO4 | Data signal |
| Pin 3 (NULL) | - | - | - | Not connected |
| Pin 4 (GND) | Black | Pin 6 | GND | Ground |

### Pull-up Resistor (Optional but Recommended)

Add a **4.7kΩ - 10kΩ resistor** between VCC (Pin 1) and DATA (Pin 2) for reliable communication.

```
DHT22 Pin 1 (VCC) ──┬────── RPi Pin 1 (3.3V)
                    │
                  [4.7kΩ]
                    │
DHT22 Pin 2 (DATA) ─┴────── RPi Pin 7 (GPIO4)

DHT22 Pin 4 (GND) ────────── RPi Pin 6 (GND)
```

**Note**: Many DHT22 modules come with a built-in pull-up resistor on the PCB. Check your module's datasheet.

## Raspberry Pi GPIO Pinout (First 10 Pins)

```
┌─────────────────────────────┐
│  Raspberry Pi GPIO Header   │
│  (View from above)          │
└─────────────────────────────┘

 3.3V  [ 1] [ 2]  5V
GPIO2  [ 3] [ 4]  5V
GPIO3  [ 5] [ 6]  GND    ← Ground (DHT22 Pin 4)
GPIO4  [ 7] [ 8]  GPIO14 ← Data (DHT22 Pin 2)
  GND  [ 9] [10]  GPIO15

      (continues...)
```

## Visual Wiring Diagram

```
┌────────────────────────────────────────┐
│      Raspberry Pi 3/4/5                │
│                                        │
│  [1] 3.3V ────────────────┐           │
│  [2] 5V                   │           │
│  [3] GPIO2                │           │
│  [4] 5V                   │           │
│  [5] GPIO3                │           │
│  [6] GND ─────────────┐   │           │
│  [7] GPIO4 ────────┐  │   │           │
│  [8] GPIO14        │  │   │           │
│  [9] GND           │  │   │           │
│  [10] GPIO15       │  │   │           │
│   ...              │  │   │           │
└────────────────────┼──┼───┼───────────┘
                     │  │   │
              Yellow │  │   │ Red
               (Data)│  │   │(VCC)
                     │  │   │
               ┌─────┴──┴───┴─────┐
               │  Pin: 2  4   1   │
               │  DHT22 Sensor    │
               │  ░░░░░░░░░░░░░░░ │
               │                  │
               └──────────────────┘
                 Black (GND)
```

## Software Configuration

The RPI Lab project is configured to use **GPIO4 (BCM numbering)** for the DHT22 data line.

### Default Configuration
- **GPIO Pin**: GPIO4 (physical pin 7)
- **Library**: Adafruit_DHT
- **Sensor Type**: DHT22 (AM2302)

### Changing GPIO Pin

To use a different GPIO pin, edit `sensors/dht22.py`:

```python
# Default GPIO pin for DHT22 data line (BCM numbering)
DEFAULT_DHT_PIN = 4  # Change this to your desired GPIO number
```

Or modify `gui/rpi_gui.py`:

```python
# Initialize DHT22 sensor (change GPIO pin here)
DHT_SENSOR = DHT22Sensor(gpio_pin=4)  # Change to desired pin
```

## Installation Steps

1. **Physical Connection**:
   - Power off Raspberry Pi
   - Connect DHT22 to Raspberry Pi following the wiring diagram above
   - Optionally add 4.7kΩ pull-up resistor between VCC and DATA
   - Double-check all connections
   - Power on Raspberry Pi

2. **Software Installation**:
   ```bash
   # Install system dependencies
   sudo apt-get update
   sudo apt-get install -y libgpiod2 python3-dev
   
   # Install Python library
   cd /opt/rpi-lab
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Test Sensor**:
   ```bash
   # Test DHT22 reading
   cd /opt/rpi-lab
   source .venv/bin/activate
   python3 sensors/dht22.py
   ```

   Expected output:
   ```
   Reading from DHT22 sensor on GPIO4...
   Temperature: 23.5°C
   Humidity: 45.2%
   ```

4. **Use in GUI**:
   - Launch RPI Lab GUI
   - Touch "🌡️ Sensor Readings" button
   - View temperature and humidity readings
   - Touch "🔄 Refresh" to update readings

## Troubleshooting

### Problem: "N/A" readings in GUI

**Possible Causes**:
1. DHT22 not connected or loose connection
2. Wrong GPIO pin configuration
3. Missing pull-up resistor
4. Faulty DHT22 sensor

**Solutions**:
- Verify all wiring connections
- Check GPIO pin number in configuration
- Add 4.7kΩ pull-up resistor if not present
- Test with `python3 sensors/dht22.py` to see detailed errors
- Try a different DHT22 sensor

### Problem: Permission errors

**Solution**:
```bash
# Add user to gpio group
sudo usermod -a -G gpio mrmagic
sudo reboot
```

### Problem: Import error "No module named 'Adafruit_DHT'"

**Solution**:
```bash
cd /opt/rpi-lab
source .venv/bin/activate
pip install Adafruit-DHT==1.4.0
```

## Advanced: Multiple DHT22 Sensors

To add multiple DHT22 sensors, connect each DATA pin to a different GPIO pin:

```python
# In gui/rpi_gui.py
DHT_SENSOR_1 = DHT22Sensor(gpio_pin=4)   # Living room
DHT_SENSOR_2 = DHT22Sensor(gpio_pin=17)  # Bedroom
DHT_SENSOR_3 = DHT22Sensor(gpio_pin=27)  # Outside
```

## References

- [DHT22 Datasheet](https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf)
- [Adafruit DHT Library Documentation](https://github.com/adafruit/Adafruit_Python_DHT)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [BCM vs Board GPIO Numbering](https://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering)

## Safety Notes

⚠️ **Important**:
- Always power off Raspberry Pi before connecting/disconnecting sensors
- Double-check wiring before powering on
- DHT22 operates at 3.3V but is 5V tolerant
- Never connect VCC directly to a GPIO pin (use 3.3V or 5V power pins)
- Incorrect wiring can damage the sensor or Raspberry Pi

## License

This documentation is part of the RPI Lab project. See LICENSE file for details.
