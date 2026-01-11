# Troubleshooting Guide

Common issues and solutions for RPI Lab.

## GUI Issues

### GUI Won't Start

**Symptom:** GUI doesn't appear on boot

**Check:**
```bash
sudo systemctl status rpi_gui.service
sudo journalctl -u rpi_gui.service -n 50
```

**Solutions:**

1. **X11 not running:**
```bash
ps aux | grep Xorg
systemctl status lightdm
sudo systemctl restart lightdm
```

2. **Wrong DISPLAY variable:**
```bash
echo $DISPLAY    # Should be :0
export DISPLAY=:0
```

3. **Service not enabled:**
```bash
sudo systemctl enable rpi_gui.service
sudo systemctl start rpi_gui.service
```

### GUI Crashes Repeatedly

**Check logs for errors:**
```bash
sudo journalctl -u rpi_gui.service --no-pager -b
```

**Common causes:**

1. **Sensor disconnected:** Check I2C wiring
2. **Dependencies missing:** Reinstall venv
```bash
sudo /opt/rpi-lab/install/venv_setup.sh
```

3. **Permissions:** Add user to groups
```bash
sudo usermod -a -G i2c,gpio $USER
# Log out and back in
```

## Sensor Issues

### BME690 Not Detected

**Check I2C:**
```bash
i2cdetect -y 1
```

Should show device at 0x76 or 0x77.

**Solutions:**

1. **I2C not enabled:**
```bash
sudo raspi-config nonint do_i2c 0
sudo reboot
```

2. **Wrong wiring:** Verify connections
```
BME690 → Pi
VCC → Pin 1 (3.3V)
SDA → Pin 3 (GPIO2)
SCL → Pin 5 (GPIO3)
GND → Pin 6 (GND)
```

3. **Wrong I2C bus:** Try bus 0
```bash
i2cdetect -y 0
```

### Sensor Readings Show "N/A"

**Check permissions:**
```bash
groups    # Should include i2c
ls -la /dev/i2c-1
```

**Fix:**
```bash
sudo usermod -a -G i2c $USER
# Log out and log back in
```

**Test sensor directly:**
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 sensors/bme690.py
```

### Gas Alerts Too Frequent

**Symptom:** Constant beeping during normal operation

**Cause:** Threshold too high or sensor warming up

**Solution:** Wait 5-10 minutes for sensor stabilization

Gas alert threshold: < 5kΩ (only "Gas Detected" level triggers beeping)

Normal operation: > 60kΩ

### Humidity Readings Seem Low

**⚠️ IMPORTANT: READ THIS FIRST BEFORE ADJUSTING!**

**Symptom:** BME690 humidity reads lower than a cheap sensor (DHT11/DHT22/other)

**STOP! The BME680/688 is likely CORRECT:**
- BME680/688 accuracy: ±3%RH (Bosch datasheet - see docs/BME680.pdf)
- Cheap sensors (DHT11/DHT22): often read 10-20%RH **too high**
- Gas heater impact: only 1-3%RH, NOT 30%RH
- **Do not disable gas heater** - it's needed for sensor accuracy and compensation

**Verify First:**

1. **Salt calibration test (definitive reference):**
```bash
# Create saturated salt solution in sealed container
# NaCl (table salt) saturated solution = exactly 75%RH at 20°C
# Place BME690 sensor in container for 8+ hours
# Reading should be 73-77%RH (within ±3%RH tolerance)
```

2. **Check environment validity:**
- 38%RH at 4.5°C is **normal** for winter indoor air
- 38%RH at 20°C might indicate dry heating system (also normal)
- Compare to weather station outdoor humidity readings

3. **Question your reference sensor:**
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 sensors/test_humidity_calibration.py
# Compare BME690 to your "reference" - which is more plausible?
```

**Only calibrate if:**
- Salt test shows consistent error (e.g., reads 70%RH in 75%RH environment)
- You have a lab-grade hygrometer (not a cheap sensor)

**Calibration (only after verification):**
```bash
# For MQTT publisher
sudo systemctl edit mqtt_publisher.service --full
# Add under [Service]:
Environment="BME690_HUM_OFFSET=5.0"    # Add 5%RH
# OR
Environment="BME690_HUM_SCALE=1.1"     # Multiply by 1.1

sudo systemctl daemon-reload
sudo systemctl restart mqtt_publisher.service rpi_gui.service
```

**DO NOT DO THIS:**
- ❌ Disable gas heater (`BME690_ENABLE_GAS=0`) - reduces accuracy
- ❌ Calibrate based on cheap DHT11/DHT22 sensors
- ❌ Assume 70%RH is "correct" for all environments
- ❌ Apply large offsets (>10%RH) without salt test verification

**Note:** See [docs/BME680.pdf](BME680.pdf) for official Bosch specifications and accuracy tolerances.

## Touch Issues

### Touch Not Responding

**Check touch device:**
```bash
cat /proc/bus/input/devices | grep -A 5 ft5x06
```

**Test touch:**
```bash
sudo evtest /dev/input/event2
```

**Solutions:**

1. **Touch driver not loaded:**
```bash
sudo /opt/rpi-lab/display/fix_touch_detection.sh
sudo reboot
```

2. **Wrong overlay:** Check `/boot/firmware/config.txt`
```
dtoverlay=edt-ft5406,polling_mode
```

### Touch Coordinates Wrong

**Check display config:**
```bash
grep waveshare /boot/firmware/config.txt
```

Should have:
```
dtoverlay=vc4-kms-dsi-waveshare-800x480
```

## TUI Issues

### Aliases Not Found

**Reload configuration:**
```bash
source ~/.bash_aliases
```

**Or restart SSH session:**
```bash
exit
ssh user@pi-ip
```

**Create manually if missing:**
```bash
echo "alias rpi-tui='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py'" >> ~/.bash_aliases
source ~/.bash_aliases
```

### TUI Colors Not Displaying

**Check terminal:**
```bash
echo $TERM    # Should support 256 colors
```

**Fix:**
```bash
export TERM=xterm-256color
```

## Deployment Issues

### Deployment Hangs

**Check internet:**
```bash
ping github.com
```

**Check SSH to GitHub:**
```bash
ssh -T git@github.com
```

**Check disk space:**
```bash
df -h
```

Need at least 500MB free.

### Git Errors

**Corrupted objects:**
```bash
cd /opt/rpi-lab
sudo git fsck --full
sudo git fetch --all
sudo git reset --hard origin/main
```

**Permission denied:**
```bash
sudo chown -R root:root /opt/rpi-lab
```

## Speaker Issues

### No Sound

**Check speaker wiring:**
```
Speaker → Pi
Red (+) → Pin 32 (GPIO12)
Black (-) → Pin 6/9 (GND)
```

**Test speaker:**
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 sensors/speaker.py
```

**Check GPIO permissions:**
```bash
groups    # Should include gpio
```

## Network Issues

### Network Info Shows "N/A"

**Check network interfaces:**
```bash
ip addr show eth0
ip addr show wlan0
```

**Restart network:**
```bash
sudo systemctl restart NetworkManager
```

## Performance Issues

### High CPU Usage

**Check processes:**
```bash
top
htop
```

**Reduce TUI refresh rate:**
```bash
rpi-tui --interval 5.0    # Slower updates
```

### GUI Slow/Laggy

1. **Disable 3D acceleration:** Comment out in `/boot/firmware/config.txt`
```
#dtoverlay=vc4-kms-v3d
```

2. **Check sensor read errors:**
```bash
sudo journalctl -u rpi_gui.service | grep -i error
```

## Recovery Mode

### Complete Reset

```bash
# 1. Backup data
sudo cp -a /opt/rpi-lab /opt/rpi-lab.backup

# 2. Remove installation
sudo rm -rf /opt/rpi-lab

# 3. Reinstall
git clone https://github.com/user/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/install_gui.sh
sudo reboot
```

## Getting Help

1. **Check logs:**
```bash
sudo journalctl -u rpi_gui.service -n 100
```

2. **Test components individually:**
- BME690: `python3 sensors/bme690.py`
- Speaker: `python3 sensors/speaker.py`
- TUI: `rpi-tui-sensor`

3. **Check hardware:**
- `i2cdetect -y 1` for I2C devices
- `evtest` for touch
- `groups` for permissions

4. **Review documentation:**
- [INSTALLATION.md](INSTALLATION.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [SERVICE_MANAGEMENT.md](SERVICE_MANAGEMENT.md)

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Permission denied /dev/i2c-1" | Not in i2c group | `sudo usermod -a -G i2c $USER` |
| "Cannot open display :0" | X11 not running | Check lightdm service |
| "BME690 not found" | Sensor disconnected | Check wiring, I2C config |
| "Touch device not found" | Touch driver issue | Run fix_touch_detection.sh |
| "Module not found: bme690" | Venv not activated | `source .venv/bin/activate` |
