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

### Humidity Readings Too Low

**Symptom:** BME690 humidity reads 10-20%RH lower than GUI or reference meters

**Root Cause:** BME680/690 gas heater warms sensor and lowers humidity readings

**Solutions:**

1. **Disable gas heater** (recommended for accurate humidity):
```bash
# For GUI service
sudo systemctl edit rpi_gui.service --full
# Add under [Service]:
Environment="BME690_ENABLE_GAS=0"

# For MQTT publisher
sudo systemctl edit mqtt_publisher.service --full
# Add under [Service]:
Environment="BME690_ENABLE_GAS=0"

sudo systemctl daemon-reload
sudo systemctl restart rpi_gui.service mqtt_publisher.service
```

2. **Apply humidity calibration** (if heater must stay on):
```bash
# Example: add 18%RH offset
sudo systemctl edit rpi_gui.service --full
# Add under [Service]:
Environment="BME690_HUM_OFFSET=18.0"

# Or apply scaling factor (e.g., 1.2x)
Environment="BME690_HUM_SCALE=1.2"

sudo systemctl daemon-reload
sudo systemctl restart rpi_gui.service
```

3. **Test calibration values**:
```bash
# Run sensor test with env vars
cd /opt/rpi-lab
source .venv/bin/activate
BME690_ENABLE_GAS=0 python3 sensors/bme690.py
# Compare output to reference meter

# Try different offsets
BME690_HUM_OFFSET=15.0 python3 sensors/bme690.py
BME690_HUM_OFFSET=20.0 python3 sensors/bme690.py
```

**Note:** Humidity calibration applies to TUI, MQTT, and GUI simultaneously. Set env vars in all service files for consistency.

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
