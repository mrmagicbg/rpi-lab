# Installation Guide

Complete installation guide for RPI Lab system.

## Hardware Requirements

- Raspberry Pi 4/5 (3B+ may work)
- Waveshare 4.3" DSI LCD Rev 2.2 (800×480)
- BME690 sensor (I2C address 0x76)
- PWM speaker (GPIO 12)
- CC1101 RF module (optional, for TPMS)

## Quick Install (10 minutes)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip rsync i2c-tools python3-smbus

# 2. Clone repository
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab

# 3. Install components
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh         # Python environment
sudo /opt/rpi-lab/install/display_install.sh    # Display + touch
sudo /opt/rpi-lab/install/install_gui.sh        # GUI + auto-start
sudo /opt/rpi-lab/install/install_rf.sh         # RF (optional)

# 4. Enable I2C and reboot
sudo raspi-config nonint do_i2c 0
sudo reboot
```

## Component Details

### Python Virtual Environment

Located at `/opt/rpi-lab/.venv/`

Installs:
- bme690 sensor library
- smbus2 for I2C
- RPi.GPIO for PWM
- rich for TUI display
- evdev for touch input

### Display Setup

Configures Waveshare 4.3" DSI LCD with:
- 800×480 resolution
- ft5x06 touch controller
- Polling mode for reliability

Config location: `/boot/firmware/config.txt`

### GUI Service

Auto-starts on boot via systemd:
- Service: `rpi_gui.service`
- User: Current user
- Display: :0 (X11)
- Groups: i2c, gpio

### TUI Aliases

Automatically creates in `~/.bash_aliases`:
```bash
alias rpi-tui='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py'
alias rpi-tui-sensor='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --sensor'
alias rpi-tui-rf='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --rf'
```

## BME690 Sensor Wiring

```
BME690          Raspberry Pi
─────────────────────────────
VCC (3.3V)  →   Pin 1 (3.3V)
SDA         →   Pin 3 (GPIO2)
SCL         →   Pin 5 (GPIO3)
GND         →   Pin 6 (GND)
```

I2C address: 0x76 (default) or 0x77 (with ADDR jumper)

Verify: `i2cdetect -y 1`

## Speaker Wiring

```
Speaker         Raspberry Pi
─────────────────────────────
Red (+)     →   Pin 32 (GPIO12)
Black (-)   →   Pin 6/9 (GND)
```

Hardware PWM on GPIO12 for clean 2kHz tones.

## Testing

### BME690 Sensor
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 sensors/bme690.py
```

### Speaker
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 sensors/speaker.py
```

### TUI
```bash
ssh user@pi-ip
rpi-tui-sensor
```

### GUI
- Should auto-start on boot
- Check: `sudo systemctl status rpi_gui.service`

## Post-Install Checklist

- [ ] BME690 detected at 0x76: `i2cdetect -y 1`
- [ ] User in i2c group: `groups`
- [ ] Touch responds: `sudo evtest /dev/input/event2`
- [ ] GUI auto-starts on boot
- [ ] TUI aliases work over SSH
- [ ] Speaker produces sound
- [ ] Network info displays correctly

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.
