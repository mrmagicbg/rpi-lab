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

#### 1. Pull Latest Code

On your Pi:
```bash
cd ~/rpi-lab
git pull origin main
sudo rsync -av ~/rpi-lab/ /opt/rpi-lab/
```

#### 2. Run MQTT Installer

```bash
sudo /opt/rpi-lab/install/install_mqtt.sh
```

**You'll be prompted for:**
- **MQTT Broker URL:** your-ha-external-url.com
- **MQTT Port:** 1883 (or 8883 for TLS)
- **MQTT Username:** mqtt_user
- **MQTT Password:** your_secure_password_here
- **Device Name:** rpi_lab (or custom name)
- **Update Interval:** 60 (seconds)

#### 3. Verify Service

```bash
# Check service status
sudo systemctl status mqtt_publisher.service

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

Edit service file:
```bash
sudo nano /etc/systemd/system/mqtt_publisher.service
```

Change:
```ini
Environment="UPDATE_INTERVAL=30"
```

Restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart mqtt_publisher.service
```

### Change MQTT Broker

Edit service file and update:
```ini
Environment="MQTT_BROKER=new-broker.com"
Environment="MQTT_PORT=1883"
```

Restart service.

### Use Different Device Name

Edit service file:
```ini
Environment="DEVICE_NAME=bedroom_pi"
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

3. **On Pi - Update service:**
```ini
Environment="MQTT_PORT=8883"
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

```yaml
automation:
  - alias: "RPI Lab Gas Detected"
    trigger:
      platform: numeric_state
      entity_id: sensor.rpi_lab_gas_resistance
      below: 5000
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
