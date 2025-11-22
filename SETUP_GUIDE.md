# Raspberry Pi + CC1101 Setup Guide

Complete guide for configuring and using the CC1101 radio module with Raspberry Pi for capturing **TPMS signals (433 MHz FSK)** and **IoT signals (868 MHz OOK, e.g. TFA Dostmann IT+)**.

---

## 🛠️ Hardware Wiring

| CC1101 Pin | Raspberry Pi Pin | GPIO Number | Notes |
|------------|------------------|-------------|-------|
| **VCC**    | Pin **17**       | —           | 3.3 V only ⚠️ |
| **GND**    | Pin **20**       | —           | Ground |
| **SCK**    | Pin **23**       | GPIO 11     | SPI Clock |
| **MOSI**   | Pin **19**       | GPIO 10     | SPI Master Out |
| **MISO**   | Pin **21**       | GPIO 9      | SPI Master In |
| **CSN**    | Pin **24**       | GPIO 8      | Chip Select |
| **GDO0**   | Pin **22**       | GPIO 25     | Optional interrupt |
| **GDO2**   | Pin **22**       | GPIO 25     | Packet sync signal |

⚠️ **Critical:** Always use **Pin 17 (3.3 V)** for VCC. Never connect CC1101 to 5 V - it will destroy the module!

---

## 🖥️ Software Setup

### 1. Enable SPI Interface

```bash
sudo raspi-config
```
Navigate to: `Interface Options` → `SPI` → Enable

Or edit directly:
```bash
sudo nano /boot/firmware/config.txt
```
Add:
```
dtparam=spi=on
```
Reboot:
```bash
sudo reboot
```

Verify SPI is enabled:
```bash
ls -l /dev/spidev*
# Should show: /dev/spidev0.0 /dev/spidev0.1
```

### 2. Install Dependencies

**For Raspberry Pi OS (Debian/Raspbian):**
```bash
sudo apt update
sudo apt install git build-essential wiringpi -y
```

**For Kali Linux on Raspberry Pi:**
```bash
sudo apt update
sudo apt install git build-essential -y

# Install WiringPi manually (if not in repos)
cd ~
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
./build
```

**Alternative: Download WiringPi package directly**
```bash
# For 64-bit ARM
wget https://github.com/WiringPi/WiringPi/releases/download/3.6/wiringpi_3.6_arm64.deb
sudo dpkg -i wiringpi_3.6_arm64.deb

# For 32-bit ARM
wget https://github.com/WiringPi/WiringPi/releases/download/3.6/wiringpi_3.6_armhf.deb
sudo dpkg -i wiringpi_3.6_armhf.deb
```

Verify installation:
```bash
gpio -v
# Should show version info
```

### 3. Clone Repository

```bash
cd ~
git clone https://github.com/mrmagicbg/rf-lab.git
cd rf-lab/CC1101
```

### 4. Build Tools

**Build profile demo tool:**
```bash
cd ~/rf-lab/CC1101
g++ -o rx_profile_demo rx_profile_demo.cpp cc1100_raspi.cpp -lwiringPi
chmod +x rx_profile_demo
```

**Build original RX/TX demos (optional):**
```bash
g++ -o RX_Demo RX_Demo.cpp cc1100_raspi.cpp -lwiringPi
g++ -o TX_Demo TX_Demo.cpp cc1100_raspi.cpp -lwiringPi
chmod +x RX_Demo TX_Demo
```

### 5. Test Installation

```bash
# Show help (requires sudo for SPI access)
sudo ./rx_profile_demo -h

# Test TPMS profile
sudo ./rx_profile_demo -mTPMS

# Test IoT profile
sudo ./rx_profile_demo -mIoT
```

---

## 🧪 RF Profiles

### 🚗 TPMS Profile (Mode 0x07)

**Target:** Automotive tire pressure monitoring systems (Siemens VDO, Schrader)

```cpp
static uint8_t cc1100_TPMS[CFG_REGISTER] = {
  0x29, 0x2E, 0x06, 0x47, 0xD3, 0x91, 0x0A, 0x04, 0x05, 0x00,
  0x00, 0x0C, 0x00, 0x10, 0xB0, 0x71, 0x5B, 0xF8, 0x13, 0xA0,
  0xF8, 0x47, 0x07, 0x0C, 0x18, 0x1D, 0x1C, 0xC7, 0x00, 0xB2,
  0x02, 0x26, 0x09, 0xB6, 0x04, 0xED, 0x2B, 0x16, 0x11, 0x4B,
  0x00, 0x59, 0x7F, 0x3C, 0x81, 0x3F, 0x0B
};
```

**Specifications:**
- Frequency: **433.92 MHz** (ISM band)
- Modulation: **2-FSK**
- Encoding: **Manchester**
- Bitrate: ~19.2 kbps
- Deviation: ~47 kHz
- RX Bandwidth: 135–200 kHz
- Sync Word: Often absent → use async mode or preamble 0x55 0x55 0x55 0x56
- Packet Length: 10 bytes (fixed or variable)

**Usage:**
```bash
sudo ./rx_profile_demo -mTPMS -addr 1 -channel 0
```

**Notes:**
- TPMS sensors typically transmit every 60-120 seconds when stationary
- Transmission rate increases when vehicle is moving or pressure changes
- Use GDO0 for raw bitstream capture if sync word detection fails

---

### 🏠 IoT Profile (Mode 0x08)

**Target:** TFA Dostmann IT+ weather station sensors (868 MHz OOK)

```cpp
static uint8_t cc1100_IoT[CFG_REGISTER] = {
  0x29, 0x2E, 0x06, 0x47, 0xD3, 0x91, 0xFF, 0x04, 0x05, 0x00,
  0x00, 0x08, 0x00, 0x21, 0x62, 0x76, 0xF5, 0x83, 0x13, 0x22,
  0xFB, 0x15, 0x07, 0x30, 0x18, 0xEC, 0x03, 0x40, 0x91, 0x87,
  0x68, 0xFB, 0x56, 0x00, 0xE9, 0x24, 0x00, 0x11, 0x41, 0x00,
  0x59, 0x7F, 0x3F, 0x81, 0x3F, 0x0B
};
```

**Specifications:**
- Frequency: **868.3 MHz** (center of IT+ band)
- Modulation: **ASK/OOK**
- Encoding: None (raw OOK pulses)
- Bitrate: ~2.4–4.8 kbps
- RX Bandwidth: 58–100 kHz
- Sync Word: Often 0xD3 0x91 or preamble 0xAA
- Packet Length: Variable (often 3–5 bytes)

**Usage:**
```bash
sudo ./rx_profile_demo -mIoT -addr 1 -channel 0
```

**Supported Sensors:**
- Indoor/outdoor temperature sensors
- Humidity sensors
- Rain gauges
- Wind speed/direction

**Notes:**
- Sensors typically transmit every 30-60 seconds
- Short burst transmissions (~10-20ms)
- Use packet mode first, fallback to async if decoding fails

---

## 🔧 Profile Switching Implementation

Profiles are switched in `cc1100_raspi.cpp` via the `set_mode()` function:

```cpp
void CC1100::set_mode(uint8_t mode)
{
    switch (mode)
    {
        case 0x01:
            spi_write_burst(WRITE_BURST, cc1100_GFSK_1_2_kb, CFG_REGISTER);
            break;
        case 0x02:
            spi_write_burst(WRITE_BURST, cc1100_GFSK_38_4_kb, CFG_REGISTER);
            break;
        case 0x03:
            spi_write_burst(WRITE_BURST, cc1100_GFSK_100_kb, CFG_REGISTER);
            break;
        case 0x06:
            spi_write_burst(WRITE_BURST, cc1100_OOK_4_8_kb, CFG_REGISTER);
            break;
        case 0x07: // TPMS profile (433.92 MHz Manchester 2-FSK)
            spi_write_burst(WRITE_BURST, cc1100_TPMS, CFG_REGISTER);
            break;
        case 0x08: // IoT TFA IT+ profile (868.3 MHz OOK)
            spi_write_burst(WRITE_BURST, cc1100_IoT, CFG_REGISTER);
            break;
        default:
            spi_write_burst(WRITE_BURST, cc1100_GFSK_100_kb, CFG_REGISTER);
            break;
    }
}
```

CLI argument parsing in `rx_profile_demo.cpp`:

```cpp
if(strcmp(argv[i], "-mTPMS") == 0) { 
    mode = 0x07; 
    freq = 0x02; // 433 MHz
}
else if(strcmp(argv[i], "-mIoT") == 0) { 
    mode = 0x08; 
    freq = 0x03; // 868 MHz
}
```

---

## 🧪 Testing and Usage

### Health Check

Verify CC1101 communication:
```bash
sudo ./rx_profile_demo -mTPMS
```

Expected output:
```
Init CC1100...
Partnumber: 0x00
Version   : 0x14
...done!
Applied profile mode=0x07 freq_sel=2 channel=0 addr=1
```

### TPMS Capture

```bash
# Basic TPMS reception
sudo ./rx_profile_demo -mTPMS

# With custom settings
sudo ./rx_profile_demo -mTPMS -addr 1 -channel 0 -freq 2

# Dump register configuration
sudo ./rx_profile_demo -mTPMS
# (Shows register dump after initialization)
```

**Trigger TPMS transmission:**
- Drive the vehicle
- Deflate/inflate tire slightly
- Wait 60-120 seconds for periodic transmission

### IoT Sensor Capture

```bash
# Basic IoT reception
sudo ./rx_profile_demo -mIoT

# With custom settings
sudo ./rx_profile_demo -mIoT -addr 1 -channel 0 -freq 3
```

**Monitor output:**
- Sensors typically transmit every 30-60 seconds
- Check battery levels (weak batteries = intermittent transmissions)
- Ensure sensors are within ~50m range

### Two-Way Testing (TX/RX)

**Receiver (Pi #1):**
```bash
sudo ./RX_Demo -v -a3 -c1 -f434 -m100
```

**Transmitter (Pi #2):**
```bash
sudo ./TX_Demo -v -a1 -r3 -i1000 -t5 -c1 -f434 -m100
```

---

## 🛠️ Makefile (Optional)

Create `CC1101/Makefile`:

```makefile
CC = g++
CFLAGS = -Wall -I.
LIBS = -lwiringPi

all: rx_profile_demo RX_Demo TX_Demo

rx_profile_demo: rx_profile_demo.cpp cc1100_raspi.cpp
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

RX_Demo: RX_Demo.cpp cc1100_raspi.cpp
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

TX_Demo: TX_Demo.cpp cc1100_raspi.cpp
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

clean:
	rm -f rx_profile_demo RX_Demo TX_Demo *.o

.PHONY: all clean
```

**Usage:**
```bash
make              # Build all
make rx_profile_demo  # Build profile demo only
make clean        # Remove binaries
```

---

## 🐛 Troubleshooting

### No SPI devices found
```bash
# Check if SPI is enabled
ls -l /dev/spidev*

# Enable via raspi-config
sudo raspi-config
# Interface Options → SPI → Enable → Reboot
```

### CC1101 not detected (Version: 0x00 or 0xFF)
- Check wiring (especially GND and 3.3V)
- Verify CSN (Pin 24) is connected
- Ensure CC1101 module is not damaged
- Check for loose connections on breadboard

### No packets received
- Verify antenna is connected to CC1101
- Check frequency matches transmitter
- Confirm modulation profile is correct
- Increase debug level: `radio.set_debug_level(1)`
- Dump registers: `radio.show_register_settings()`

### WiringPi issues
```bash
# Check WiringPi installation
gpio -v

# Reinstall if needed
sudo apt remove wiringpi
wget https://github.com/WiringPi/WiringPi/releases/download/3.6/wiringpi_3.6_arm64.deb
sudo dpkg -i wiringpi_3.6_arm64.deb
```

### Permission denied on /dev/spidev
```bash
# Add user to spi group
sudo usermod -a -G spi $USER
# Log out and back in

# Or run with sudo
sudo ./rx_profile_demo -mTPMS
```

### TPMS signals not detected
- Trigger sensor manually (deflate/inflate tire)
- Check local regulations (TPMS frequencies vary by region: 315 MHz USA, 433 MHz EU)
- Try adjusting RX bandwidth in register config
- Verify 433.92 MHz antenna is installed

### IoT sensors intermittent
- Check sensor battery levels
- Verify 868 MHz is legal in your region
- Wait for transmission interval (30-60s)
- Ensure sensor is within range (~50m max)

---

## 📚 Additional Resources

- [CC1101 Datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
- [SmartRF Studio](https://www.ti.com/tool/SMARTRFTM-STUDIO) - Register configuration tool
- [WiringPi Documentation](http://wiringpi.com/)
- [Original CC1101 Library](https://github.com/SpaceTeddy/CC1101)
- [RF Lab Repository](https://github.com/mrmagicbg/rf-lab)

---

## ✅ Quick Reference

**Mode IDs:**
- `0x01` = GFSK 1.2kb
- `0x02` = GFSK 38.4kb
- `0x03` = GFSK 100kb (default)
- `0x04` = MSK 250kb
- `0x05` = MSK 500kb
- `0x06` = OOK 4.8kb
- `0x07` = **TPMS (433.92 MHz FSK Manchester)**
- `0x08` = **IoT IT+ (868.3 MHz OOK)**

**Frequency Select:**
- `1` = 315 MHz
- `2` = 433 MHz
- `3` = 868 MHz (default)
- `4` = 915 MHz

**Essential Commands:**
```bash
# TPMS capture
sudo ./rx_profile_demo -mTPMS

# IoT capture
sudo ./rx_profile_demo -mIoT

# Show help
sudo ./rx_profile_demo -h

# Build all tools
cd ~/rf-lab/CC1101
make
```

---

**Last Updated:** 2025-11-23  
**Version:** 1.0.0
