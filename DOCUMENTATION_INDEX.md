# RPI Lab - BME690 Sensor Documentation Index

## 🎯 Getting Started (Pick One)

### Quick Start (5 minutes)
👉 **[docs/BME690_WIRING.md](docs/BME690_WIRING.md)** - Wiring diagram and I2C setup

### Complete Setup (15 minutes)
👉 **[docs/BME690_SETUP.md](docs/BME690_SETUP.md)** - Step-by-step installation and testing

## 📚 Detailed Documentation

### Hardware & Wiring
- 📖 **[docs/BME690_WIRING.md](docs/BME690_WIRING.md)**
  - Raspberry Pi 3 wiring (3V3, GND, SDA, SCL)
  - I2C address selection (0x76/0x77)
  - Enabling I2C and group permissions

### Project Overview
- 📖 **[README.md](README.md)** - Main project documentation
  - BME690 sensor setup section
  - Installation instructions
  - GUI features overview
  - Deployment workflow

### Installation Status
- 📖 **[UPDATES_COMPLETE.md](UPDATES_COMPLETE.md)** - Update summary

## 🔧 Code Reference

### Core Sensor Module
- `sensors/bme690.py` - BME690 sensor implementation with dry-run support

### Installation Scripts
- `install/venv_setup.sh` - Virtual environment setup (adds i2c tools)
- `install/install_gui.sh` - GUI and system dependencies (adds i2c group)
- `install/display_install.sh` - Display and touch setup

### Configuration
- `requirements.txt` - Python package dependencies (bme690)
- `gui/rpi_gui.service` - systemd service file (I2C group + dry-run env)
- `README.md` - Full project documentation

## ⚡ Quick Commands

### Installation
```bash
# One-time setup on Raspberry Pi
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/install_gui.sh
sudo raspi-config nonint do_i2c 0   # enable I2C
sudo reboot
```

### Testing
```bash
# Test BME690 sensor directly (dry-run enabled by service)
cd /opt/rpi-lab
source .venv/bin/activate
python3 -m sensors.bme690
```

### Service Management
```bash
# View GUI status
sudo systemctl status rpi_gui.service

# View live logs
sudo journalctl -u rpi_gui.service -f

# Restart service
sudo systemctl restart rpi_gui.service
```

## 🐛 Troubleshooting

### Sensor shows "N/A"
**Solution**: Check I2C wiring and address
- 3V3 (Pin 1) ✓
- GND (Pin 9) ✓
- SDA (Pin 3 / GPIO2) ✓
- SCL (Pin 5 / GPIO3) ✓
- Address: default 0x76; cut ADDR trace for 0x77

### Permission denied on /dev/i2c-1
**Solution**: Add user to i2c group
```bash
sudo usermod -a -G i2c mrmagic
# Log out and back in
```

## 📋 File Structure

```
rpi-lab/
├── 🔧 sensors/
│   └── bme690.py                     ← Sensor module
├── 🖥️  gui/
│   ├── rpi_gui.py                    ← GUI (BME690 integrated)
│   └── rpi_gui.service               ← Service file (dry-run + i2c)
├── 📦 install/
│   ├── venv_setup.sh                 ← Venv setup (i2c tools)
│   ├── install_gui.sh                ← GUI installer (i2c group)
│   ├── display_install.sh            ← Display setup
│   └── install_rf.sh                 ← RF hardware setup
├── 📚 docs/
│   ├── BME690_SETUP.md               ← Setup guide
│   ├── BME690_WIRING.md              ← Wiring reference
│   └── TPMS_MONITORING.md            ← TPMS monitor docs
├── 🚀 deploy/
│   ├── deploy.sh                     ← Full deployment
│   └── quick_deploy.sh               ← Quick update
├── 📄 README.md                      ← Project overview
└── requirements.txt                  ← Dependencies (updated)
```

## 🔗 Related Documentation

- **TPMS RF Monitor**: [docs/TPMS_MONITORING.md](docs/TPMS_MONITORING.md)
- **Display Setup**: `install/display_install.sh`
- **GitHub Deployment**: `deploy/deploy.sh`

## 💬 Support

→ Pimoroni BME690 Python library: https://github.com/pimoroni/bme690-python
→ Product page & datasheet: https://shop.pimoroni.com/products/bme690-breakout

→ See [DHT22_QUICK_REFERENCE.md](DHT22_QUICK_REFERENCE.md)

## ✅ Status

- ✅ DHT22 module fully implemented with modern library
- ✅ GUI integration complete and tested
- ✅ Installation scripts updated
- ✅ Service configuration optimized
- ✅ Comprehensive documentation provided
- ✅ Ready for production deployment

## 📊 Summary

| Component | Status | File |
|-----------|--------|------|
| Sensor Module | ✅ Updated | `sensors/dht22.py` |
| GUI Integration | ✅ Ready | `gui/rpi_gui.py` |
| Installation | ✅ Updated | `install/venv_setup.sh` |
| Service Config | ✅ Updated | `gui/rpi_gui.service` |
| Documentation | ✅ Complete | `docs/DHT22_SETUP.md` |

---

**Last Updated**: December 28, 2025  
**Status**: ✅ Ready for Deployment  
**Repository**: https://github.com/mrmagicbg/rpi-lab
