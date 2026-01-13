# Home Assistant MQTT Integration

Complete guide for integrating BME690 sensor data with Home Assistant via MQTT.

## Overview

This integration publishes BME690 sensor data (temperature, humidity, pressure, gas resistance) from your remote Raspberry Pi to Home Assistant using MQTT protocol with auto-discovery.

**Features:**
- Auto-discovery in Home Assistant
- Real-time sensor updates (configurable interval)
- Automatic reconnection
- Systemd service for reliability
- Supports authentication
- Remote access via external URL

## Architecture

```
Remote Pi → MQTT Broker (on HA) → Home Assistant
(BME690)    Port 1883/8883        (Sensors)
```

## Prerequisites

### On Home Assistant

1. **MQTT Broker** - Install Mosquitto broker add-on
2. **MQTT Integration** - Enable MQTT integration
3. **Port Forwarding** - Forward MQTT port (1883 or 8883)

### On Remote Raspberry Pi

1. **RPI Lab installed** - See [INSTALLATION.md](INSTALLATION.md)
2. **BME690 working** - Verify with `python3 sensors/bme690.py`
3. **Internet access** - Can reach your HA external URL

## Installation Steps

### Part 1: Home Assistant Setup

#### 1. Install Mosquitto MQTT Broker

**Via Add-on Store:**
1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Search for "Mosquitto broker"
3. Click **Install**
4. Configure (see configuration below)
5. Click **Start**
6. Enable **Start on boot**

**Mosquitto Configuration:**
```yaml
logins:
  - username: mqtt_user
    password: your_secure_password_here
require_certificate: false
certfile: fullchain.pem
keyfile: privkey.pem
```

**Notes:**
- Choose strong password
- For internet exposure, consider TLS (port 8883) - see Security section

#### 2. Configure MQTT Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "MQTT"
4. Enter broker details:
   - **Broker:** localhost (or core-mosquitto if using add-on)
   - **Port:** 1883
   - **Username:** mqtt_user
   - **Password:** your_secure_password_here
5. Click **Submit**

#### 3. Port Forwarding

**Required Port:**
- **1883** - MQTT (unencrypted)
- **8883** - MQTTS (TLS encrypted) - **Recommended for internet**

**On Your Router:**
1. Log into router admin panel
2. Find **Port Forwarding** or **NAT** settings
3. Add rule:
   - **External Port:** 1883 (or 8883 for TLS)
   - **Internal IP:** Your HA IP address
   - **Internal Port:** 1883 (or 8883 for TLS)
   - **Protocol:** TCP
4. Save and apply

**Verify Port is Open:**
```bash
# From external network
nc -zv your-ha-external-url.com 1883
```

#### 4. Firewall Rules (if applicable)

If HA has firewall enabled:
```bash
# Allow MQTT port
sudo ufw allow 1883/tcp
# Or for TLS
sudo ufw allow 8883/tcp
```

### Part 2: Raspberry Pi Setup

#### Important: Virtual Environment Paths

The MQTT publisher service runs from `/opt/rpi-lab/.venv` (production directory), **not** `~/rpi-lab/.venv` (development directory). All Python packages must be installed in the production venv.

**Common mistake:**
```bash
# ❌ Wrong - installs to dev venv
cd ~/rpi-lab
source .venv/bin/activate
pip install bme680  # Goes to ~/rpi-lab/.venv
```

**Correct:**
```bash
# ✅ Right - installs to production venv
sudo /opt/rpi-lab/.venv/bin/pip install bme680 paho-mqtt
```

#### 1. Pull Latest Code

On your Pi:
```bash
cd ~/rpi-lab
git pull origin main
sudo rsync -av ~/rpi-lab/ /opt/rpi-lab/
```

#### 2. Sync to Production & Update Dependencies

```bash
sudo rsync -av ~/rpi-lab/ /opt/rpi-lab/ --exclude '.git' --exclude '__pycache__'
```

Recreate the production venv cleanly (recommended):
```bash
cd /opt/rpi-lab
sudo rm -rf .venv
sudo python3 -m venv .venv --system-site-packages
sudo /opt/rpi-lab/.venv/bin/pip install -r requirements.txt
```

Or install just the MQTT dependencies:
```bash
sudo /opt/rpi-lab/.venv/bin/pip install bme680==2.0.0 paho-mqtt==1.6.1
```

#### 3. Configure MQTT Settings

**Option A: Interactive Configuration (Recommended)**

Run the installer to configure MQTT into the unified config file:
```bash
cd /opt/rpi-lab
sudo bash install/install_mqtt.sh
```

The script will prompt you for:
```
MQTT Broker hostname/IP: ha.mrmagic.synology.me
MQTT Port: 1883
MQTT Username: mqtt_user
MQTT Password: ********
Device Name: rpi_lab
Update Interval (seconds): 60
```

It updates the `[MQTT]` section in `/opt/rpi-lab/config/sensor.conf`, installs/updates the systemd service, and starts it.

**Option B: Manual Configuration**

Edit `/opt/rpi-lab/config/sensor.conf` and set the `[MQTT]` section:
```ini
[MQTT]
broker = ha.mrmagic.synology.me
port = 1883
username = mqtt_user
password = your_password
topic_prefix = homeassistant
device_name = rpi_lab
update_interval = 60
```

Restart to apply:
```bash
sudo systemctl restart mqtt_publisher.service
```

#### 4. Verify Service

```bash
# Check service status
sudo systemctl status mqtt_publisher.service

# View logs in real-time
sudo journalctl -u mqtt_publisher.service -f
```

**Expected log output:**
```
INFO - === BME690 MQTT Publisher Starting ===
INFO - MQTT Broker: ha.mrmagic.synology.me:1883
INFO - Device Name: rpi_lab
INFO - Update Interval: 300s
INFO - Initializing BME690 sensor...
INFO - BME690 sensor initialized successfully
INFO - MQTT authentication configured
INFO - Connecting to MQTT broker ha.mrmagic.synology.me:1883 (attempt 1/5)
INFO - Connected to MQTT broker at ha.mrmagic.synology.me:1883
INFO - Published discovery config for temperature
INFO - Published discovery config for humidity
INFO - Published discovery config for pressure
INFO - Published discovery config for gas_resistance
INFO - Starting sensor publishing loop (interval: 300s)
INFO - Published: T=23.5°C, H=45.2%, P=1013.2hPa, G=125430Ω
```

If you see `bme680 library not installed`, see [bme680 library not installed](#bme680-library-not-installed) in Troubleshooting.

#### 5. Verify in Home Assistant

# View logs
sudo journalctl -u mqtt_publisher.service -f
```

**Expected output:**
```
Connected to MQTT broker at your-ha-external-url.com:1883
Published discovery config for temperature
Published discovery config for humidity
Published discovery config for pressure
Published discovery config for gas_resistance
Published: T=23.5°C, H=45.2%, P=1013.2hPa, G=125430Ω
```

### Part 3: Verify in Home Assistant

1. Go to **Settings** → **Devices & Services** → **MQTT**
2. You should see "RPI Lab BME690" device
3. Click on it to see 4 sensors:
   - RPI Lab Temperature
   - RPI Lab Humidity
   - RPI Lab Pressure
   - RPI Lab Gas Resistance

## Configuration

### Change Update Interval

Edit the config file (recommended):
```bash
sudo nano /opt/rpi-lab/config/sensor.conf
```

Set in the `[MQTT]` section:
```ini
update_interval = 300
```

Restart:
```bash
sudo systemctl restart mqtt_publisher.service
```

### Change MQTT Broker

Edit the config file (recommended):
```bash
sudo nano /opt/rpi-lab/config/sensor.conf
```

Update the `[MQTT]` section:
```ini
broker = your-ha-hostname-or-ip
port = 1883
username = mqtt_user
password = your_password
topic_prefix = homeassistant
```

Restart:
```bash
sudo systemctl restart mqtt_publisher.service
```

### Use Different Device Name

Edit the config file:
```bash
sudo nano /opt/rpi-lab/config/sensor.conf
```

Set in `[MQTT]`:
```ini
device_name = bedroom_pi
```

Restart the service:
```bash
sudo systemctl restart mqtt_publisher.service
```

This changes the device name in Home Assistant.

## Security Recommendations

### For Internet-Exposed MQTT

**Option 1: Use TLS/SSL (Recommended)**

1. **On Home Assistant:**
   - Obtain SSL certificate (Let's Encrypt)
   - Configure Mosquitto for TLS (port 8883)
   - Update port forwarding to 8883

2. **Mosquitto TLS Config:**
```yaml
logins:
  - username: mqtt_user
    password: strong_password
require_certificate: false
certfile: fullchain.pem
keyfile: privkey.pem
```

3. **On Pi - Update config:**
```ini
[MQTT]
port = 8883
```

**Option 2: VPN Tunnel**

Instead of exposing MQTT to internet:
- Set up WireGuard/OpenVPN on HA
- Connect Pi via VPN
- Use internal MQTT (localhost:1883)
- No port forwarding needed

**Option 3: Reverse Proxy**

- Use nginx/Apache as reverse proxy
- Terminate SSL at proxy
- Forward to MQTT broker internally

### Additional Security

1. **Strong Passwords:** Use 20+ character random passwords
2. **Fail2ban:** Install fail2ban for MQTT
3. **Monitor Logs:** Regular log review for suspicious activity
4. **Restrict IP:** If possible, whitelist Pi's IP range

## Troubleshooting

### bme680 library not installed

**Error:**
```
ERROR - bme680 library not installed (pip install bme680)
ERROR - BME690 sensor not available - check I2C connection
```

**Cause:** Libraries installed in wrong virtual environment. The service uses `/opt/rpi-lab/.venv`, not `~/rpi-lab/.venv`.

**Solution:**
```bash
# Install in the production venv (what service uses)
/opt/rpi-lab/.venv/bin/pip install bme680 paho-mqtt

# Or recreate the venv cleanly
cd /opt/rpi-lab
sudo rm -rf .venv
sudo python3 -m venv .venv --system-site-packages
sudo /opt/rpi-lab/.venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl restart mqtt_publisher.service
```

### Connection Failed

**Check logs:**
```bash
sudo journalctl -u mqtt_publisher.service -n 50
```

**Common issues:**

1. **Wrong URL/Port:**
```
Error: Connection refused
Solution: Verify MQTT_BROKER and MQTT_PORT
```

2. **Authentication Failed:**
```
Error: Return code: 5
Solution: Check MQTT_USER and MQTT_PASSWORD
```

3. **Firewall Blocking:**
```bash
# Test from Pi
telnet your-ha-url.com 1883
# Should connect
```

4. **Port Not Forwarded:**
```bash
# Test from external network
nc -zv your-ha-url.com 1883
```

### Sensors Not Appearing in HA

1. **Check MQTT integration enabled** in HA
2. **View MQTT traffic:**
   - Settings → Devices & Services → MQTT → Configure
   - Listen to topic: `homeassistant/#`
3. **Verify discovery messages sent** (check Pi logs)
4. **Restart HA** to force discovery refresh

**After v3.0.10 Update (Gas Resistance Units Changed):**

If upgrading from older version, gas resistance unit changed from Ω to kΩ:

1. **Remove old entity** (Settings → Devices & Services → MQTT → RPI Lab BME690 → Delete gas resistance entity)
2. **Restart MQTT publisher** to resend discovery:
```bash
sudo systemctl restart mqtt_publisher.service
```
3. **Force rediscovery** in HA (Settings → MQTT → Configure → Reload)
4. **Update automations** if they reference gas resistance thresholds:
   - Old: `below: 5000` (Ω) → New: `below: 5` (kΩ)

### Old Data or No Updates

1. **Check service is running:**
```bash
sudo systemctl status mqtt_publisher.service
```

2. **Verify BME690 sensor:**
```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 sensors/bme690.py
```

3. **Check update interval** in service file

### High CPU Usage

Reduce update frequency:
```ini
Environment="UPDATE_INTERVAL=300"  # 5 minutes
```

## Home Assistant Automation Examples

### Temperature Alert

```yaml
automation:
  - alias: "RPI Lab High Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.rpi_lab_temperature
      above: 30
    action:
      service: notify.mobile_app
      data:
        message: "RPI Lab temperature is {{ states('sensor.rpi_lab_temperature') }}°C"
```

### Gas Detection Alert

**Note:** As of v3.0.10, gas resistance is published in kΩ (not Ω).

```yaml
automation:
  - alias: "RPI Lab Gas Detected"
    trigger:
      platform: numeric_state
      entity_id: sensor.rpi_lab_gas_resistance
      below: 5  # kΩ (5000 Ω)
    action:
      service: notify.persistent_notification
      data:
        title: "Gas Detected!"
        message: "RPI Lab detected volatile gases"
```

### Dashboard Card

```yaml
type: entities
title: RPI Lab Sensors
entities:
  - entity: sensor.rpi_lab_temperature
  - entity: sensor.rpi_lab_humidity
  - entity: sensor.rpi_lab_pressure
  - entity: sensor.rpi_lab_gas_resistance
```

## Advanced Configuration

### Custom Topics

Edit `/opt/rpi-lab/sensors/mqtt_publisher.py`:
```python
MQTT_TOPIC_PREFIX = 'my_custom_prefix'
```

### Multiple Sensors

To publish multiple Pis:
- Use different `DEVICE_NAME` for each Pi
- Each will appear as separate device in HA

### QoS Levels

For higher reliability, edit `mqtt_publisher.py`:
```python
self.client.publish(topic, payload, qos=1)  # QoS 1 for guaranteed delivery
```

## Uninstall

```bash
# Stop and disable service
sudo systemctl stop mqtt_publisher.service
sudo systemctl disable mqtt_publisher.service

# Remove service file
sudo rm /etc/systemd/system/mqtt_publisher.service
sudo systemctl daemon-reload

# Remove from Home Assistant
# Settings → Devices & Services → MQTT → RPI Lab BME690 → Delete
```

## Port Forwarding Quick Reference

| Service | Port | Protocol | Forward To | Notes |
|---------|------|----------|------------|-------|
| MQTT | 1883 | TCP | HA IP:1883 | Unencrypted |
| MQTTS | 8883 | TCP | HA IP:8883 | TLS encrypted (recommended) |

**Router Configuration:**
```
External: your-ha-url.com:1883 → Internal: 192.168.x.x:1883
```

## Support

- **MQTT Issues:** Check Mosquitto logs in HA
- **Sensor Issues:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Service Issues:** `sudo journalctl -u mqtt_publisher.service -f`

## See Also

- [INSTALLATION.md](INSTALLATION.md) - RPI Lab installation
- [SERVICE_MANAGEMENT.md](SERVICE_MANAGEMENT.md) - Service management
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment workflow
