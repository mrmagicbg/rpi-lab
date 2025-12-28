# RPI Lab DHT22 Sensor Deployment Checklist

Use this checklist to verify your DHT22 sensor is properly installed and integrated with the GUI.

## Hardware Setup ✓

- [ ] DHT22 sensor module obtained and tested
- [ ] **Wiring verified:**
  - [ ] Pin 1 (VCC) → Raspberry Pi Pin 1 (3.3V)
  - [ ] Pin 2 (DATA) → Raspberry Pi Pin 7 (GPIO4)
  - [ ] Pin 4 (GND) → Raspberry Pi Pin 6 (GND)
  - [ ] Pin 3 (NULL) left unconnected
- [ ] All jumper wires securely connected
- [ ] Optional: 4.7kΩ pull-up resistor installed (between VCC and DATA)
- [ ] Sensor powered on (check if module has LED)

## Software Installation ✓

### System Level

- [ ] Raspberry Pi OS updated:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

- [ ] System dependencies installed:
  ```bash
  sudo apt-get install -y python3-full python3-dev build-essential git
  ```

### RPI Lab Setup

- [ ] Repository cloned:
  ```bash
  git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
  ```

- [ ] Copied to /opt:
  ```bash
  sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
  ```

- [ ] Virtual environment created:
  ```bash
  sudo /opt/rpi-lab/install/venv_setup.sh
  ```

- [ ] Python dependencies installed (gpiozero, RPi.GPIO, etc.):
  ```bash
  pip install -r requirements.txt
  ```

## Sensor Testing ✓

### Quick Test

- [ ] Test sensor module is working:
  ```bash
  cd /opt/rpi-lab
  source .venv/bin/activate
  python3 -m sensors.dht22
  ```

- [ ] Output shows temperature and humidity (not "N/A"):
  ```
  Reading from DHT22 sensor on GPIO4...
  Temperature: XX.X°C
  Humidity: YY.Y%
  ```

### Troubleshooting (if test failed)

- [ ] Check wiring with multimeter:
  - [ ] 3.3V on Pin 1
  - [ ] 0V on Pin 6
  - [ ] DATA pin toggling on Pin 7

- [ ] Test alternate GPIO pin (if available):
  - [ ] Edit `sensors/dht22.py` line 20
  - [ ] Change `DEFAULT_DHT_PIN = 17` (example)
  - [ ] Re-run test

- [ ] Add 4.7kΩ pull-up resistor if needed:
  - [ ] Between Pin 1 (VCC) and Pin 7 (GPIO4/DATA)

- [ ] Check for GPIO permission issues:
  ```bash
  sudo usermod -a -G gpio $(whoami)
  # Log out and back in
  ```

## GUI Integration ✓

### GUI Installation

- [ ] Display and X11 dependencies installed:
  ```bash
  sudo /opt/rpi-lab/install/display_install.sh
  ```

- [ ] GUI dependencies installed:
  ```bash
  sudo /opt/rpi-lab/install/install_gui.sh
  ```

### Service Configuration

- [ ] GUI service enabled:
  ```bash
  sudo systemctl enable rpi_gui.service
  ```

- [ ] GPIO group permissions configured:
  ```bash
  sudo usermod -a -G gpio mrmagic
  ```

- [ ] Sudoers configured for reboot:
  ```bash
  sudo cat /etc/sudoers.d/rpi-lab
  ```

### Manual Service Start

- [ ] Service starts manually without errors:
  ```bash
  sudo systemctl start rpi_gui.service
  ```

- [ ] Service status is "active (running)":
  ```bash
  sudo systemctl status rpi_gui.service
  ```

- [ ] Check service logs for errors:
  ```bash
  sudo journalctl -u rpi_gui.service -n 20
  ```

## GUI Testing ✓

### Visual Inspection

- [ ] GUI appears on display (fullscreen)
- [ ] Title bar shows "RPI Lab Control Panel"
- [ ] Sensor display visible at top:
  - [ ] 🌡️ Temperature reading in red
  - [ ] 💧 Humidity reading in cyan
  - [ ] Status shows "✓ Last updated: HH:MM:SS" (not error)

### Sensor Data Verification

- [ ] Temperature reading is reasonable (15-35°C for room temp)
- [ ] Humidity reading is reasonable (20-80% for indoor)
- [ ] Readings update every 5 seconds (check timestamp)
- [ ] No "N/A" or warning messages

### Button Functionality

- [ ] 📡 TPMS Monitor button works (if RF hardware installed)
- [ ] 🔄 Reboot System button responds to touch
- [ ] 💻 Open Terminal button opens terminal window
- [ ] ❌ Exit Application button shows confirmation dialog

## Auto-Start Configuration ✓

- [ ] Service runs automatically on boot:
  ```bash
  sudo reboot
  # After reboot, GUI should appear automatically
  ```

- [ ] Service continues running after GUI restart:
  ```bash
  sudo systemctl restart rpi_gui.service
  sudo systemctl status rpi_gui.service
  ```

## Production Deployment ✓

- [ ] All checklist items completed
- [ ] Sensor readings are stable and accurate
- [ ] GUI is responsive and reliable
- [ ] Service auto-starts on reboot
- [ ] Backups are current:
  ```bash
  ls -lh /opt/backups/
  ```

- [ ] Deployment script tested:
  ```bash
  cd ~/rpi-lab
  git add .
  git commit -m "Initial DHT22 sensor deployment"
  git push origin main
  ```

### Scheduled Maintenance

- [ ] Weekly: Check sensor logs for errors
  ```bash
  sudo journalctl -u rpi_gui.service --since "24 hours ago" | grep ERROR
  ```

- [ ] Monthly: Verify sensor accuracy (compare with reference)
- [ ] Quarterly: Check for library updates
  ```bash
  pip list --outdated
  ```

## Rollback Plan (If Issues Occur)

If serious issues occur, rollback to previous working state:

```bash
# List available backups
ls -lh /opt/backups/

# Restore backup (if available)
sudo rm -rf /opt/rpi-lab
sudo cp -a /opt/backups/rpi-lab-backup-YYYYMMDD-HHMMSS /opt/rpi-lab
sudo systemctl restart rpi_gui.service

# Re-enable service
sudo systemctl enable rpi_gui.service
```

## Documentation ✓

- [ ] Configuration documented:
  - [ ] GPIO pin used: **4**
  - [ ] Sensor location: ______
  - [ ] Installation date: ______

- [ ] Relevant documentation read:
  - [ ] [DHT22_SETUP.md](DHT22_SETUP.md) - Hardware & software setup
  - [ ] [../README.md](../README.md) - Project overview & deployment
  - [ ] `deploy/deploy.sh` - Full deployment options

## Notes

Use this section to document any customizations or issues:

```
Additional GPIO pins used: _________________________
Special wiring notes: ______________________________
Sensor location/mounting: __________________________
Known issues: ______________________________________
Performance observations: __________________________
```

---

**Deployment Date:** ______________________  
**Deployed By:** ______________________  
**Verified By:** ______________________  
**Notes:** _________________________________________________________
