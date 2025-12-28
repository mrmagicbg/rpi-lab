# DHT22 Temperature & Humidity Sensor Setup Guide

## Overview

This guide covers wiring, software setup, and troubleshooting for the DHT22 (AM2302) sensor on Raspberry Pi.

## Hardware Requirements

- **DHT22 sensor module** (also known as AM2302)
- **3 jumper wires** minimum (4 if using external pull-up resistor)
- **Optional: 4.7kΩ pull-up resistor** (some boards have built-in)
- **Raspberry Pi** (any model with GPIO pins)

## Wiring

### Standard Wiring (No External Pull-up)

DHT22 modules typically have built-in pull-up resistors. Connect as follows:

```
DHT22 Module        Raspberry Pi GPIO
───────────────────────────────────────
Pin 1 (VCC)    →    Pin 1 (3.3V)
Pin 2 (DATA)   →    Pin 7 (GPIO4 BCM)
Pin 3 (NULL)   →    Not connected
Pin 4 (GND)    →    Pin 6 (GND)
```

### With External Pull-up Resistor

If your module doesn't have a pull-up, add a 4.7kΩ resistor:

```
DHT22 Module        Raspberry Pi GPIO
───────────────────────────────────────
Pin 1 (VCC)    →    Pin 1 (3.3V)
Pin 2 (DATA)   →    Pin 7 (GPIO4 BCM)
                │
              [4.7kΩ] (optional pull-up)
                │
            Pin 1 (3.3V)
Pin 3 (NULL)   →    Not connected
Pin 4 (GND)    →    Pin 6 (GND)
```

### Physical Pin Layout Reference

```
          [USB Power]
                │
           ┌────┴────┐
        2V5 │1      2│ 5V      ← Use Pin 1 for VCC
        SDA │3      4│ 5V
        SCL │5      6│ GND     ← Use Pin 6 for GND
    GPIO4 ◄─│7      8│ GPIO14
        GND │9     10│ GPIO15
    GPIO17 │11    12│ GPIO18
    GPIO27 │13    14│ GND
    GPIO22 │15    16│ GPIO23
        3V3 │17    18│ GPIO24
    GPIO10 │19    20│ GND
     GPIO9 │21    22│ GPIO25
    GPIO11 │23    24│ GPIO8
        GND │25    26│ GPIO7
            └────────┘
```

**Key Pins:**
- **Pin 1**: 3.3V (VCC) - Power supply
- **Pin 6**: GND (Ground)
- **Pin 7**: GPIO4 (BCM) - Default data pin for DHT22

## Software Setup

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-full python3-dev build-essential git
```

### 2. Clone and Setup RPI Lab

```bash
cd ~
git clone https://github.com/mrmagicbg/rpi-lab.git
cd rpi-lab
```

### 3. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `gpiozero==2.0.1` - GPIO control library
- `RPi.GPIO` - Low-level GPIO access
- Other dependencies (evdev, rich, loguru)

## Testing

### Quick Test (Verify Connection)

```bash
cd ~/rpi-lab
source .venv/bin/activate
python3 -m sensors.dht22
```

**Expected output (sensor working):**
```
2025-12-28 16:56:36,408 - __main__ - INFO - DHT22 sensor initialized on GPIO4
Reading from DHT22 sensor on GPIO4...
Temperature: 23.5°C
Humidity: 45.2%
```

### Troubleshooting Test Failures

| Output | Problem | Solution |
|--------|---------|----------|
| `N/A / N/A` | Sensor not responding | Check wiring, verify GPIO4 pins connected |
| `checksum failed` | Data corruption | Shorten wires, add pull-up resistor |
| `sensor timeout` | Takes too long to respond | Move away from electrical interference |
| `permission denied` | GPIO access issue | Run with `sudo`, or add user to `gpio` group |

### Adding Current User to GPIO Group

```bash
sudo usermod -a -G gpio $(whoami)
# Log out and back in for change to take effect
```

## Using DHT22 in GUI

### Automatic (Service Auto-start)

The DHT22 sensor display is built into the main GUI, which auto-starts on boot:

1. Install GUI (one-time):
   ```bash
   sudo bash install/install_gui.sh
   sudo reboot
   ```

2. GUI appears on boot automatically
3. Sensor readings shown at top of screen:
   - 🌡️ Temperature (red)
   - 💧 Humidity (cyan)
   - Auto-updates every 5 seconds

### Manual Testing

```bash
source /opt/rpi-lab/.venv/bin/activate
DISPLAY=:0 python3 /opt/rpi-lab/gui/rpi_gui.py
```

## Configuration

### Changing GPIO Pin

Default: **GPIO4** (Physical Pin 7)

To use a different pin:

1. Edit `sensors/dht22.py` (line 20):
   ```python
   DEFAULT_DHT_PIN = 17  # Change to your GPIO number
   ```

2. Edit `gui/rpi_gui.py` (line 37):
   ```python
   DHT_SENSOR = DHT22Sensor(gpio_pin=17)  # Match the above
   ```

3. Restart GUI service:
   ```bash
   sudo systemctl restart rpi_gui.service
   ```

### Changing Update Interval

Default: **5 seconds** between readings

Edit `gui/rpi_gui.py` (find `update_sensor_readings` method):

```python
# Change 5000 (milliseconds) to desired interval
self.root.after(5000, self.update_sensor_readings)  # 5 seconds
```

## Technical Details

### DHT22 Sensor Specifications

| Parameter | Value |
|-----------|-------|
| **Temperature Range** | -40°C to +80°C |
| **Temperature Accuracy** | ±0.5°C |
| **Humidity Range** | 0% to 100% |
| **Humidity Accuracy** | ±2% RH |
| **Sampling Rate** | Minimum 2 seconds |
| **Power Supply** | 3.3V DC |
| **Current Draw** | ~2.5mA typical |
| **Protocol** | 1-Wire (custom timing) |

### Data Format

The sensor sends 40 bits of data:
- **Bits 0-15**: Humidity (16-bit integer + decimal)
- **Bits 16-31**: Temperature (16-bit integer + decimal)
- **Bits 32-39**: Checksum (8-bit)

### Reading Protocol

1. Master sends start signal (20ms low pulse)
2. Sensor pulls low, then high for response
3. Sensor sends 40 bits using pulse width encoding
   - Bit 0 = short high pulse (~25μs)
   - Bit 1 = long high pulse (~70μs)
4. Checksum verified for data integrity

## Common Issues & Solutions

### Issue: "No response" or constant timeout

**Cause**: GPIO not initialized correctly or sensor not powered

**Solutions**:
- Check 3.3V on Pin 1 with multimeter
- Verify GND connection on Pin 6
- Try a different GPIO pin
- Run with `sudo` for full access

### Issue: Checksum errors (valid readings then failure)

**Cause**: Electrical noise or wire interference

**Solutions**:
- Shorten sensor wires (keep < 1 meter)
- Add 4.7kΩ pull-up resistor
- Move away from RF sources (WiFi, RF modules)
- Use shielded wire if available
- Reduce read frequency in code

### Issue: GUI shows "N/A" for readings

**Cause**: Sensor library not installed or GPIO permission issue

**Solutions**:
- Check venv activated: `source .venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`
- Add user to gpio group: `sudo usermod -a -G gpio mrmagic`
- Check service logs: `sudo journalctl -u rpi_gui.service -f`

### Issue: Permission Denied when reading GPIO

**Cause**: User doesn't have GPIO permissions

**Solutions**:
- Run as `sudo` temporarily
- Add user to gpio group (see above)
- Configure sudoers (see install/install_gui.sh)

## Debugging Commands

```bash
# Test GPIO access
gpio -v  # Install gpio command if needed: sudo apt install wiringpi

# Check current GPIO state
cat /sys/class/gpio/gpio4/value  # 0=low, 1=high

# Monitor sensor readings continuously
watch 'cd ~/rpi-lab && source .venv/bin/activate && python3 -m sensors.dht22'

# Check service logs
sudo journalctl -u rpi_gui.service -f

# Test GPIO directly with Python
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)
print(f"GPIO4 is: {GPIO.input(4)}")
GPIO.cleanup()
EOF
```

## References

- [DHT22 Datasheet](https://www.rototron.info/dht22-tutorial-for-raspberry-pi/)
- [RPi.GPIO Documentation](https://pypi.org/project/RPi.GPIO/)
- [gpiozero Documentation](https://gpiozero.readthedocs.io/)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `sudo journalctl -u rpi_gui.service -f`
3. Test sensor directly: `python3 -m sensors.dht22`
4. Check wiring against diagrams in this guide
