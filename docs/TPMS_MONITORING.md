# TPMS Monitor - Tire Pressure Monitoring System

## Overview

The TPMS Monitor provides real-time visualization of tire pressure sensor data captured via CC1101 RF transceiver. It decodes and displays pressure, temperature, battery status, and sensor IDs from TPMS sensors used in vehicles.

## Supported Protocols

### Schrader (EG53MA4, G4, etc.)
- **Frequency**: 315 MHz / 433.92 MHz
- **Encoding**: Manchester
- **Data**: 32-bit sensor ID, 16-bit pressure (kPa × 4), 8-bit temperature (°C + 40), battery status
- **Common in**: US, European, Japanese vehicles

### Siemens/VDO (Continental)
- **Frequency**: 433.92 MHz
- **Encoding**: Manchester
- **Data**: 32-bit sensor ID, 16-bit pressure (kPa - 100)/100, 8-bit temperature (°C + 50), battery status
- **Common in**: European vehicles (BMW, Mercedes, Audi, VW, etc.)

### Generic Manchester
- Attempts to decode unknown TPMS protocols
- Extracts sensor ID and attempts pressure/temperature decoding

## Hardware Requirements

### CC1101 RF Transceiver Module
- **Connection**: SPI (Raspberry Pi GPIO)
- **Antenna**: 433 MHz (17.3 cm wire for quarter-wave)
- **Wiring**:
  ```
  CC1101 Pin    → Raspberry Pi GPIO
  VCC (3.3V)    → Pin 1 (3.3V)
  GND           → Pin 6 (GND)
  MOSI          → Pin 19 (GPIO 10, MOSI)
  MISO          → Pin 21 (GPIO 9, MISO)
  SCK           → Pin 23 (GPIO 11, SCLK)
  CSN (CS)      → Pin 24 (GPIO 8, CE0)
  GDO0          → Pin 22 (GPIO 25)
  GDO2          → (optional, not used)
  ```

### Enable SPI
```bash
sudo raspi-config
# Interface Options → SPI → Enable
# Or edit /boot/firmware/config.txt:
dtparam=spi=on
```

Verify: `ls /dev/spidev*` should show `/dev/spidev0.0` and `/dev/spidev0.1`

## Software Components

### 1. TPMS Decoder (`rf/tpms_decoder.py`)
Python module for decoding TPMS protocols:
- Manchester bit-level decoding
- Schrader protocol parser
- Siemens/VDO protocol parser
- Generic fallback decoder
- Pressure/temperature unit conversion
- CSV log file parser

**Example Usage**:
```python
from rf.tpms_decoder import TPMSDecoder

decoder = TPMSDecoder()
reading = decoder.decode_packet(raw_bytes, rssi=-60, lqi=100)

if reading:
    print(f"Sensor: {reading.sensor_id}")
    print(f"Pressure: {reading.pressure_psi:.1f} PSI")
    print(f"Temperature: {reading.temperature_c:.1f}°C")
    print(f"Battery: {'LOW' if reading.battery_low else 'OK'}")
```

### 2. TPMS Monitor GUI (`rf/tpms_monitor_gui.py`)
Real-time visualization application:
- Live sensor display with cards for each detected sensor
- Start/Stop RF capture controls
- Activity log with packet details
- Automatic sensor ID tracking
- Pressure (PSI/kPa) and temperature (°C/°F) display
- Battery and signal strength indicators

**Standalone Launch**:
```bash
cd /opt/rpi-lab/rf
python tpms_monitor_gui.py
```

**From Main GUI**: Click "📡 TPMS Monitor" button

### 3. TPMS Logger (`rf/tpms_logger.py`)
Session-based logging with CSV and JSON export:
- Automatic session file naming with timestamps
- CSV export with pressure/temperature/battery/RSSI data
- JSON export with summary statistics
- Session analysis tools
- Calculates min/max/avg values
- Tracks warning counts (low battery, abnormal pressure)

**Example Usage**:
```python
from rf.tpms_logger import TPMSLogger
from rf.tpms_decoder import TPMSReading

# Create logger (default: ~/rpi-lab/logs/tpms/)
logger = TPMSLogger()

# Add readings during capture session
logger.add_reading(reading)

# Export at end of session
files = logger.export_all()  # Returns {'csv': path, 'json': path}

# Get summary
summary = logger.get_summary()
print(f"Logged {summary['reading_count']} readings from {summary['unique_sensors']} sensors")
```

**Log Locations**:
- Default: `~/rpi-lab/logs/tpms/`
- Format: `tpms_session_YYYYMMDD_HHMMSS.csv` / `.json`

**Pressure Status Classification**:
- **CRITICAL**: < 26 PSI (< 179 kPa) - Red indicator
- **LOW**: 26-28 PSI (179-193 kPa) - Orange indicator
- **NORMAL**: 28-44 PSI (193-303 kPa) - Green indicator
- **HIGH**: > 44 PSI (> 303 kPa) - Yellow indicator

### 4. RF Capture Tool (`rf/CC1101/rx_profile_demo`)
C++ binary for CC1101 radio control:
- TPMS mode (433.92 MHz, Manchester encoding)
- IoT mode (868 MHz, OOK/FSK)
- Generic GFSK/OOK modes
- CSV packet logging
- Real-time console output

**Build**:
```bash
sudo bash /opt/rpi-lab/install/install_rf.sh
```

**Manual Usage**:
```bash
cd /opt/rpi-lab/rf/CC1101
sudo ./rx_profile_demo -mTPMS        # Start TPMS capture
sudo ./rx_profile_demo -mIoT         # IoT mode
sudo ./rx_profile_demo -h            # Help
```

## Usage Guide

### Quick Start

1. **Install RF tools** (if not already done):
   ```bash
   sudo bash /opt/rpi-lab/install/install_rf.sh
   ```

2. **Launch TPMS Monitor**:
   - From main GUI: Click "📡 TPMS Monitor" button
   - Or standalone: `python /opt/rpi-lab/rf/tpms_monitor_gui.py`

3. **Start Capture**:
   - Click "▶️ Start Capture" button
   - Monitor will listen for TPMS signals on 433.92 MHz

4. **Trigger TPMS Sensors**:
   - Drive vehicle (sensors transmit every ~60 seconds while moving)
   - Or use TPMS activation tool (handheld 125 kHz LF trigger)
   - Or deflate/inflate tire slightly (triggers immediate transmission)

5. **View Results**:
   - Detected sensors appear as cards
   - Shows pressure, temperature, battery, signal strength
   - Activity log shows all packets received

### Testing Without Vehicle

**Simulate TPMS packet** (for development):
```python
from rf.tpms_decoder import TPMSDecoder

# Simulated Schrader packet
test_packet = bytes([
    0x12, 0x34, 0x56, 0x78,  # Sensor ID
    0x00,                      # Status
    0x03, 0x20,                # Pressure: 800/4 = 200 kPa (29 PSI)
    0x50,                      # Temperature: 80-40 = 40°C
    0xAB                       # CRC
])

decoder = TPMSDecoder()
result = decoder.decode_packet(test_packet, rssi=-60, lqi=100)
print(result.to_dict())
```

## Troubleshooting

### No RF Binary Found
**Error**: "rx_profile_demo not found! Build it first."

**Solution**:
```bash
sudo bash /opt/rpi-lab/install/install_rf.sh
```

### SPI Not Enabled
**Error**: "Failed to init CC1101 (check wiring/SPI)"

**Check SPI**:
```bash
ls /dev/spidev*
# Should show: /dev/spidev0.0 /dev/spidev0.1
```

**Enable SPI**:
```bash
sudo raspi-config
# → Interface Options → SPI → Yes
sudo reboot
```

### No Sensors Detected
**Possible causes**:
1. **CC1101 not connected** - Check wiring
2. **Wrong frequency** - TPMS uses 433.92 MHz (US/EU) or 315 MHz (US)
3. **Sensors not transmitting** - Drive vehicle or use activation tool
4. **Antenna issue** - Ensure 17.3 cm wire connected to ANT pin
5. **Range too far** - Get within ~5 meters of vehicle

**Test CC1101**:
```bash
cd /opt/rpi-lab/rf/CC1101
sudo ./rx_profile_demo -h
# Should show help without errors
```

### Decoding Errors
**Symptom**: Packets received but not decoded

**Check**:
- Activity log shows "Unknown packet" messages
- Protocol may not be Schrader/Siemens
- Try running `rx_profile_demo` in terminal to see raw hex
- Check CSV logs in `rf/logs/` directory

**Debug**:
```bash
# Enable debug logging
cd /opt/rpi-lab/rf
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from tpms_decoder import TPMSDecoder
decoder = TPMSDecoder()
# Test with your packet hex
"
```

## Technical Details

### TPMS Transmission Patterns

**Schrader**:
- Transmits every 60 seconds while moving
- Immediate transmission on pressure change >7 kPa
- Battery life: 5-10 years

**Siemens/VDO**:
- Transmits every 60 seconds while moving
- Immediate transmission on rapid pressure loss
- Battery life: 7-10 years

### Pressure Ranges

**Normal tire pressure**:
- Passenger cars: 200-250 kPa (29-36 PSI)
- SUVs/trucks: 220-280 kPa (32-41 PSI)
- High-performance: 250-300 kPa (36-44 PSI)

**Warning thresholds**:
- Low: <180 kPa (26 PSI)
- Critical: <150 kPa (22 PSI)

### Data Format Examples

**Schrader Packet** (9 bytes after Manchester decode):
```
Byte 0-3: Sensor ID (0x12345678)
Byte 4:   Status/flags (0x00 = battery OK)
Byte 5-6: Pressure (0x0320 = 800, /4 = 200 kPa)
Byte 7:   Temperature (0x50 = 80, -40 = 40°C)
Byte 8:   CRC
```

**Siemens Packet** (9 bytes):
```
Byte 0-3: Sensor ID (0xABCDEF01)
Byte 4-5: Pressure (0x2710 = 10000, /100+100 = 200 kPa)
Byte 6:   Temperature (0x5A = 90, -50 = 40°C)
Byte 7:   Status (bit 0 = battery low)
Byte 8:   CRC
```

## CSV Log Format

Logs saved to `rf/logs/packets-mode0x07-YYYYMMDD-HHMMSS.csv`:

```csv
timestamp,mode,raw_len,raw_hex,decoded,fields
2025-12-22 18:45:30,0x07,9,12345678003200050AB,9 bytes,id=12345678,pressure=200,temp=40
```

**Fields**:
- `timestamp`: Date/time of capture
- `mode`: CC1101 mode (0x07 = TPMS)
- `raw_len`: Raw packet length in bytes
- `raw_hex`: Raw packet data (hex)
- `decoded`: Decoding result summary
- `fields`: Extracted sensor data

## References

- **CC1101 Datasheet**: Texas Instruments CC1101 Low-Power Sub-1 GHz RF Transceiver
- **TPMS Standards**: ISO 21750, FMVSS 138 (US), ECE R64 (EU)
- **Schrader Electronics**: OE TPMS supplier documentation
- **Continental/VDO**: TPMS technical specifications

## Security & Legal Notes

**Important**: 
- TPMS monitoring is **receive-only** (passive listening)
- No transmission or interference with vehicle systems
- Sensor IDs are **not** personally identifiable information
- Use only for educational/diagnostic purposes
- Comply with local radio regulations (ISM band usage)

**Privacy**: Sensor IDs are randomly assigned at manufacturing and not linked to VIN or owner information.
