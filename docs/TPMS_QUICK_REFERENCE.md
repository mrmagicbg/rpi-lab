# TPMS Monitor Quick Reference

## Launch Commands

### From Main GUI
```
Touch: "📡 TPMS Monitor" button
```

### Standalone
```bash
python /opt/rpi-lab/rf/tpms_monitor_gui.py
```

### Terminal Mode (Advanced)
```bash
cd /opt/rpi-lab/rf/CC1101
sudo ./rx_profile_demo -mTPMS
```

## CC1101 Wiring (433 MHz)

| CC1101 Pin | → | Raspberry Pi GPIO |
|------------|---|-------------------|
| VCC (3.3V) | → | Pin 1 (3.3V)      |
| GND        | → | Pin 6 (GND)       |
| MOSI       | → | Pin 19 (GPIO 10)  |
| MISO       | → | Pin 21 (GPIO 9)   |
| SCK        | → | Pin 23 (GPIO 11)  |
| CSN        | → | Pin 24 (GPIO 8)   |
| GDO0       | → | Pin 22 (GPIO 25)  |
| ANT        | → | 17.3 cm wire      |

## Enable SPI
```bash
sudo raspi-config
# → Interface Options → SPI → Yes
sudo reboot
```

## Build RF Tools
```bash
sudo bash /opt/rpi-lab/install/install_rf.sh
```

## Supported Protocols

| Protocol | Frequency | Encoding | Common In |
|----------|-----------|----------|-----------|
| Schrader | 433.92 MHz | Manchester | US, EU, Japan (Toyota, Honda, Ford, GM) |
| Siemens/VDO | 433.92 MHz | Manchester | EU (BMW, Mercedes, Audi, VW) |
| Generic | 433.92 MHz | Manchester | Unknown/Custom |

## Pressure Ranges (Normal)

| Vehicle Type | kPa | PSI |
|--------------|-----|-----|
| Passenger cars | 200-250 | 29-36 |
| SUVs/Trucks | 220-280 | 32-41 |
| High-performance | 250-300 | 36-44 |

**Warning thresholds:**
- Low: <180 kPa (26 PSI)
- Critical: <150 kPa (22 PSI)

## Triggering TPMS Sensors

1. **Drive vehicle** - Sensors transmit every ~60 seconds while moving
2. **TPMS activation tool** - 125 kHz LF trigger (handheld tool)
3. **Pressure change** - Deflate/inflate tire slightly (>7 kPa change)

## Typical Range

- **Optimal**: 1-5 meters from vehicle
- **Maximum**: Up to 10 meters with good antenna

## Troubleshooting

### No sensors detected
- Check CC1101 wiring
- Verify antenna connected (17.3 cm wire for 433 MHz)
- Ensure vehicle sensors are transmitting (drive or use activation tool)
- Check SPI enabled: `ls /dev/spidev*`

### "RF binary not found"
```bash
sudo bash /opt/rpi-lab/install/install_rf.sh
```

### "Failed to init CC1101"
- Check wiring connections
- Verify SPI enabled
- Test with: `sudo ./rx_profile_demo -h`

### Unknown protocol packets
- Check activity log for "Unknown packet" messages
- View CSV logs in `rf/logs/` directory
- May be non-TPMS 433 MHz devices (remotes, sensors, etc.)

## Button Functions

| Button | Function |
|--------|----------|
| ▶️ Start Capture | Begin RF monitoring (433.92 MHz) |
| ⏹️ Stop Capture | Stop RF monitoring |

## Display Information

Each sensor card shows:
- **Sensor ID** - 8-digit hex (e.g., 12345678)
- **Pressure** - PSI and kPa
- **Temperature** - °C and °F
- **Battery** - OK ✓ or LOW ⚠️
- **Signal** - RSSI in dBm
- **Protocol** - Schrader, Siemens/VDO, or Unknown
- **Timestamp** - Last seen time

## Log Files

CSV logs saved to: `rf/logs/packets-mode0x07-YYYYMMDD-HHMMSS.csv`

Format:
```csv
timestamp,mode,raw_len,raw_hex,decoded,fields
2025-12-22 18:45:30,0x07,9,12345678...,9 bytes,id=12345678,pressure=200,temp=40
```

## Python API Example

```python
from rf.tpms_decoder import TPMSDecoder

decoder = TPMSDecoder()
reading = decoder.decode_packet(raw_bytes, rssi=-60, lqi=100)

if reading:
    print(f"Sensor: {reading.sensor_id}")
    print(f"Pressure: {reading.pressure_psi:.1f} PSI")
    print(f"Temp: {reading.temperature_c:.1f}°C")
    print(f"Battery: {'LOW' if reading.battery_low else 'OK'}")
```

## Safety Notes

- **Receive-only** - No transmission, passive monitoring
- **No vehicle interference** - Only reads RF signals
- **Legal** - ISM band (433 MHz) allowed for receive operations
- **Privacy** - Sensor IDs are random, not linked to owner

## More Information

- Full guide: `docs/TPMS_MONITORING.md`
- Wiring: `docs/DHT22_WIRING.md` (GPIO reference)
- RF setup: `rf/SETUP_GUIDE.md`
- Changelog: `CHANGELOG.md`

---
*RPI Lab v0.4.0 - TPMS RF Monitor*
