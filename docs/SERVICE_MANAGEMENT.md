# Service Management

Systemd service management for RPI Lab GUI and MQTT publisher.

## Service File

Location: `/etc/systemd/system/rpi_gui.service`

Configuration:
- Runs after graphical.target
- User: Current user (mrmagic)
- Display: :0 (X11)
- Groups: i2c, gpio
- Auto-restart on failure

## Common Commands

### Status Check
```bash
sudo systemctl status rpi_gui.service
```

### Start/Stop/Restart
```bash
sudo systemctl start rpi_gui.service
sudo systemctl stop rpi_gui.service
sudo systemctl restart rpi_gui.service
```

### Enable/Disable Auto-Start
```bash
sudo systemctl enable rpi_gui.service    # Start on boot
sudo systemctl disable rpi_gui.service   # Don't start on boot
```

### View Logs
```bash
# Live tail
sudo journalctl -u rpi_gui.service -f

# Last 50 lines
sudo journalctl -u rpi_gui.service -n 50

# Today's logs
sudo journalctl -u rpi_gui.service --since today

# Last hour
sudo journalctl -u rpi_gui.service --since "1 hour ago"
```

### Reload Configuration
```bash
# After editing service file
sudo systemctl daemon-reload
sudo systemctl restart rpi_gui.service
```

## MQTT Publisher Service

Location: `/etc/systemd/system/mqtt_publisher.service`

Configuration:
- Runs in `/opt/rpi-lab` with venv Python
- Auto-restart on failure
- Loads MQTT and device settings from `config/sensor.conf` `[MQTT]`

### Common Commands
```bash
sudo systemctl status mqtt_publisher.service
sudo systemctl restart mqtt_publisher.service
sudo journalctl -u mqtt_publisher.service -f
```

### Change Settings
Edit `/opt/rpi-lab/config/sensor.conf`:
```ini
[MQTT]
broker = homeassistant.local
port = 1883
username =
password =
topic_prefix = homeassistant
device_name = rpi_lab
update_interval = 60
```

Apply changes:
```bash
sudo systemctl restart mqtt_publisher.service
```

## Manual GUI Launch

For testing without service:

```bash
cd /opt/rpi-lab
source .venv/bin/activate
DISPLAY=:0 python gui/rpi_gui.py
```

## Service Troubleshooting

### Service Won't Start

Check X11 is running:
```bash
ps aux | grep Xorg
echo $DISPLAY
systemctl status lightdm
```

Check permissions:
```bash
groups                    # Should include i2c, gpio
ls -la /dev/i2c-1        # Should be readable by i2c group
```

Check Python environment:
```bash
ls /opt/rpi-lab/.venv/bin/python3
/opt/rpi-lab/.venv/bin/python3 --version
```

### Service Crashes

View crash details:
```bash
sudo journalctl -u rpi_gui.service --no-pager -b
```

Common causes:
- I2C sensor disconnected
- Display not available
- Python dependencies missing
- GPIO permission issues

### Service Slow to Start

Check startup delay:
```bash
systemctl show rpi_gui.service | grep Exec
```

Service has 5-second delay to ensure X11 is ready.

## Log Interpretation

### Normal Startup
```
Started rpi_gui.service - RPI Lab GUI Application
BME690 initialized on I2C address 0x76
Speaker initialized on GPIO pin 12 (hardware PWM)
Starting RPI Lab GUI...
Screen resolution: 800x480
```

### Sensor Issues
```
BME690 read succeeded after 2 attempts
WARNING: Temperature alert! 32.5°C
ERROR: BME690 read failed after 3 attempts
```

### GUI Errors
```
ERROR: Failed to initialize GUI
WARNING: Touch device not found
ERROR: Cannot open display :0
```

## Service File Customization

Edit service file:
```bash
sudo nano /etc/systemd/system/rpi_gui.service
```

Common customizations:

**Change user:**
```ini
[Service]
User=otheruser
```

**Add environment variables:**
```ini
[Service]
Environment="BME690_DRY_RUN=1"
Environment="SPEAKER_DRY_RUN=1"
```

**Modify restart behavior:**
```ini
[Service]
Restart=always
RestartSec=5
```

After editing:
```bash
sudo systemctl daemon-reload
sudo systemctl restart rpi_gui.service
```

## See Also

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed problem solutions
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment workflow
