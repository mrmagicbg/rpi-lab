# RF Lab

Radio frequency experimentation and signal capture toolkit using TI CC1101 transceiver on Raspberry Pi.

## Overview

This repository contains CC1101 driver implementations and configuration profiles for capturing and analyzing various RF signals including automotive TPMS sensors and home IoT devices.

### Supported Profiles

| Mode | Profile | Frequency | Modulation | Bitrate | Application |
|------|---------|-----------|------------|---------|-------------|
| 0x01 | GFSK 1.2kb | 868 MHz | GFSK | 1.2 kbps | Low power IoT |
| 0x02 | GFSK 38.4kb | 868 MHz | GFSK | 38.4 kbps | Standard data |
| 0x03 | GFSK 100kb | 868 MHz | GFSK | 100 kbps | Fast data (default) |
| 0x04 | MSK 250kb | 868 MHz | MSK | 250 kbps | High speed |
| 0x05 | MSK 500kb | 868 MHz | MSK | 500 kbps | Max speed |
| 0x06 | OOK 4.8kb | 868 MHz | ASK/OOK | 4.8 kbps | Simple OOK |
| **0x07** | **TPMS** | **433.92 MHz** | **2-FSK** | **~19.2 kbps** | **Tire pressure sensors** |
| **0x08** | **IoT IT+** | **868.3 MHz** | **ASK/OOK** | **~2.4-4.8 kbps** | **TFA weather sensors** |

## Hardware Requirements

- Raspberry Pi (any model with SPI)
- TI CC1101 RF transceiver module
- WiringPi library

### Wiring

```
CC1101 <-> Raspberry Pi
Vdd    -    3.3V (Pin 1)
SI     -    MOSI (Pin 19)
SO     -    MISO (Pin 21)
CS     -    SS   (Pin 24)
SCLK   -    SCK  (Pin 23)
GDO2   -    GPIO (Pin 22)
GDO0   -    GPIO (optional, for raw capture)
GND    -    GND  (Pin 25)
```

⚠️ **Warning:** CC1101 is 3.3V only - do NOT connect to 5V!

## Quick Start

### Prerequisites

Install WiringPi (if not already installed):
```bash
sudo apt-get update
sudo apt-get install wiringpi
```

### Building

Navigate to the CC1101 directory and compile:

```bash
cd CC1101

# Build the profile demo tool
g++ -o rx_profile_demo rx_profile_demo.cpp cc1100_raspi.cpp -lwiringPi
chmod +x rx_profile_demo

# Build original RX/TX demos
g++ -o RX_Demo RX_Demo.cpp cc1100_raspi.cpp -lwiringPi
g++ -o TX_Demo TX_Demo.cpp cc1100_raspi.cpp -lwiringPi
```

### Usage Examples

#### TPMS Capture (Tire Pressure Sensors)

```bash
# Start listening for TPMS signals at 433.92 MHz
sudo ./rx_profile_demo -mTPMS

# With custom settings
sudo ./rx_profile_demo -mTPMS -addr 1 -channel 0
```

**TPMS Profile Details:**
- Frequency: 433.92 MHz (ISM band)
- Modulation: 2-FSK with Manchester encoding
- Bitrate: ~19.2 kbps
- Deviation: ~47 kHz
- RX Bandwidth: 135-200 kHz
- Common sensors: Siemens VDO, Schrader
- Packet: Typically 10 bytes (pressure, temperature, ID, battery)

#### IoT Weather Sensors (TFA IT+)

```bash
# Start listening for TFA Dostmann IT+ sensors at 868.3 MHz
sudo ./rx_profile_demo -mIoT

# With custom settings
sudo ./rx_profile_demo -mIoT -addr 1 -channel 0
```

**IoT Profile Details:**
- Frequency: 868.3 MHz (center of IT+ band)
- Modulation: ASK/OOK
- Bitrate: ~2.4-4.8 kbps
- RX Bandwidth: 58-100 kHz
- Sync: 0xD3 0x91 or preamble 0xAA
- Packet: Variable 3-5 bytes (temp, humidity, sensor ID)

#### Standard Profiles

```bash
# Fast GFSK mode (default)
sudo ./rx_profile_demo -mGFSK100 -freq 3 -channel 0

# OOK mode for simple on-off keying
sudo ./rx_profile_demo -mOOK -freq 3
```

### CLI Options

```
rx_profile_demo [-mTPMS|-mIoT|-mGFSK100|-mOOK] [options]

Modes:
  -mTPMS           TPMS profile (433.92 MHz, 2-FSK Manchester)
  -mIoT            TFA IT+ profile (868.3 MHz, OOK)
  -mGFSK100        GFSK 100kb (default)
  -mOOK            OOK 4.8kb

Options:
  -addr <dec>      Node address (default 1)
  -freq <1-4>      ISM band: 1=315, 2=433, 3=868, 4=915 MHz
  -channel <n>     Channel number (default 0)
  -h               Show help
```

## Signal Specifications

### TPMS (Mode 0x07)

**Target:** Automotive tire pressure monitoring systems

Register configuration optimized for:
- Frequency: 433.920 MHz
- Deviation: ±47 kHz
- RX Filter BW: ~200 kHz
- Data Format: Manchester encoded
- Preamble: 0x55 0x55 0x55 0x56 (or async mode)
- Sync Word: Often absent or custom

**Typical Packet Structure:**
```
[Preamble] [Sync?] [ID:4B] [Pressure:1B] [Temp:1B] [Flags:1B] [CRC:2B]
```

**Notes:**
- Most TPMS transmit every 60-120 seconds when stationary
- Increase rate when moving or pressure changes detected
- Use GDO0 for raw bitstream capture if sync fails

### TFA IT+ IoT (Mode 0x08)

**Target:** TFA Dostmann weather station sensors (IT+ protocol)

Register configuration optimized for:
- Frequency: 868.300 MHz
- Modulation: Pure OOK (on-off keying)
- Data Rate: ~3 kbps
- RX Filter BW: ~100 kHz
- Encoding: Direct pulse widths (no Manchester)

**Typical Sensors:**
- Indoor/outdoor temperature
- Humidity sensors
- Rain gauges
- Wind speed/direction

**Notes:**
- Sensors typically transmit every 30-60 seconds
- Short burst transmissions (~10-20ms)
- Fallback to async mode if packet decode fails

## Development

### Adding New Profiles

1. Generate register configuration using TI SmartRF Studio
2. Add config array to `cc1100_raspi.cpp`:
   ```cpp
   static uint8_t cc1100_MyProfile[CFG_REGISTER] = {
       0x29, 0x2E, ... // 47 register values
   };
   ```
3. Add case to `set_mode()` switch:
   ```cpp
   case 0x09: // My custom profile
       spi_write_burst(WRITE_BURST, cc1100_MyProfile, CFG_REGISTER);
       break;
   ```
4. Add CLI option to demo tool
5. Document in README

### Decoding Captured Data

Current implementation captures raw packets. Future enhancements:
- Manchester decoder for TPMS data
- OOK pulse-width decoder for IT+
- CRC validation and error correction
- Higher-level protocol parsers

## Project Structure

```
rf-lab/
├── README.md                    # This file
├── CC1101/                      # CC1101 driver and tools
│   ├── cc1100_raspi.cpp        # Main driver (with TPMS + IoT profiles)
│   ├── cc1100_raspi.h          # Driver header
│   ├── rx_profile_demo.cpp     # Profile switching demo
│   ├── RX_Demo.cpp             # Original RX demo
│   ├── TX_Demo.cpp             # Original TX demo
│   ├── README.md               # Driver-specific docs
│   └── LICENSE                 # MIT License
```

## Troubleshooting

### No packets received
1. Check wiring (especially GND and 3.3V)
2. Verify antenna is connected
3. Check frequency/modulation matches transmitter
4. Increase debug level: `radio.set_debug_level(1)`
5. Verify SPI communication: `radio.show_register_settings()`

### TPMS not detected
- Trigger sensor: deflate/inflate tire or drive vehicle
- Check local regulations (TPMS frequencies vary by region)
- Try adjusting RX bandwidth in register config

### IoT sensors intermittent
- Ensure sensors have fresh batteries
- Check sensor transmission interval (some send only on change)
- Verify 868 MHz is legal in your region

## Contributing

Contributions welcome! Areas of interest:
- Additional signal profiles (FSK, LoRa, etc.)
- Decoder implementations
- Protocol analyzers
- Power management optimizations

## Credits

This project is based on the excellent CC1101 driver library by [SpaceTeddy](https://github.com/SpaceTeddy/CC1101).

**Original Work:**
- CC1101 Arduino/Raspberry Pi driver: © 2022 SpaceTeddy
- Repository: https://github.com/SpaceTeddy/CC1101
- License: MIT

**Modifications and Additions:**
- TPMS profile (mode 0x07) for automotive tire pressure sensors
- TFA IT+ IoT profile (mode 0x08) for weather station sensors
- CLI profile switching tool (`rx_profile_demo.cpp`)
- Extended documentation and usage guides
- Custom register configurations for specialized RF capture

All modifications are released under the same MIT license as the original work.

## License

MIT License - see [LICENSE](CC1101/LICENSE) for details.

This software includes code from the CC1101 library by SpaceTeddy, which is also MIT licensed.

## Disclaimer

This software is for educational and research purposes. Ensure compliance with local RF regulations. Do not interfere with licensed spectrum or critical systems.

---

**Happy RF hunting! 📡**
