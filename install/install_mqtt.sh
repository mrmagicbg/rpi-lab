#!/bin/bash
#
# Install MQTT Publisher for Home Assistant Integration
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== Installing MQTT Publisher for Home Assistant ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# 1. Install MQTT dependencies in virtual environment
echo "Step 1: Installing Python dependencies..."
if [ -f "$PROJECT_ROOT/.venv/bin/pip" ]; then
    "$PROJECT_ROOT/.venv/bin/pip" install paho-mqtt bme680
    echo "✓ Dependencies installed (paho-mqtt, bme680)"
else
    echo "Error: Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "Run venv_setup.sh first"
    exit 1
fi

# 2. Make mqtt_publisher.py executable
echo "Step 2: Making mqtt_publisher.py executable..."
chmod +x "$PROJECT_ROOT/sensors/mqtt_publisher.py"
echo "✓ mqtt_publisher.py is executable"

# 3. Configure MQTT settings
echo "Step 3: Configuring MQTT settings..."

# Prompt for MQTT configuration
read -p "Enter MQTT Broker URL (e.g., homeassistant.example.com): " MQTT_BROKER
read -p "Enter MQTT Port [1883]: " MQTT_PORT
MQTT_PORT=${MQTT_PORT:-1883}
read -p "Enter MQTT Username: " MQTT_USER
read -sp "Enter MQTT Password: " MQTT_PASSWORD
echo
read -p "Enter Device Name [rpi_lab]: " DEVICE_NAME
DEVICE_NAME=${DEVICE_NAME:-rpi_lab}
read -p "Enter Update Interval in seconds [60]: " UPDATE_INTERVAL
UPDATE_INTERVAL=${UPDATE_INTERVAL:-60}

# Update config file
CONFIG_FILE="$PROJECT_ROOT/config/sensor.conf"
if [ -f "$CONFIG_FILE" ]; then
    # Backup original
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
    
    # Update MQTT section
    sed -i "s|^broker =.*|broker = $MQTT_BROKER|" "$CONFIG_FILE"
    sed -i "s|^port =.*|port = $MQTT_PORT|" "$CONFIG_FILE"
    sed -i "s|^username =.*|username = $MQTT_USER|" "$CONFIG_FILE"
    sed -i "s|^password =.*|password = $MQTT_PASSWORD|" "$CONFIG_FILE"
    sed -i "s|^device_name =.*|device_name = $DEVICE_NAME|" "$CONFIG_FILE"
    sed -i "s|^update_interval =.*|update_interval = $UPDATE_INTERVAL|" "$CONFIG_FILE"
    
    echo "✓ Configuration saved to $CONFIG_FILE"
else
    echo "⚠ Config file not found at $CONFIG_FILE"
    echo "  Will use defaults or environment variables"
fi

# 4. Install systemd service
echo "Step 4: Installing systemd service..."

# Create service file
SERVICE_FILE="/etc/systemd/system/mqtt_publisher.service"
cp "$PROJECT_ROOT/sensors/mqtt_publisher.service" "$SERVICE_FILE"

# Update paths to actual PROJECT_ROOT (in case not /opt/rpi-lab)
sed -i "s|WorkingDirectory=/opt/rpi-lab|WorkingDirectory=$PROJECT_ROOT|" "$SERVICE_FILE"
sed -i "s|/opt/rpi-lab/.venv/bin/python3|$PROJECT_ROOT/.venv/bin/python3|" "$SERVICE_FILE"
sed -i "s|/opt/rpi-lab/sensors/mqtt_publisher.py|$PROJECT_ROOT/sensors/mqtt_publisher.py|" "$SERVICE_FILE"

# Update user if not mrmagic
CURRENT_USER=$(logname 2>/dev/null || echo "$SUDO_USER")
if [ -n "$CURRENT_USER" ] && [ "$CURRENT_USER" != "mrmagic" ]; then
    sed -i "s|User=mrmagic|User=$CURRENT_USER|" "$SERVICE_FILE"
    echo "✓ Service configured for user: $CURRENT_USER"
fi

echo "✓ Service file created: $SERVICE_FILE"

# 5. Enable and start service
echo "Step 5: Enabling and starting service..."
systemctl daemon-reload
systemctl enable mqtt_publisher.service
systemctl start mqtt_publisher.service

echo "✓ Service enabled and started"

# 6. Show status
echo ""
echo "=== Installation Complete ==="
echo ""
echo "Service status:"
systemctl status mqtt_publisher.service --no-pager -l | head -20
echo ""
echo "View logs with:"
echo "  sudo journalctl -u mqtt_publisher.service -f"
echo ""
echo "Configuration saved to:"
echo "  $CONFIG_FILE"
echo ""
echo "Settings:"
echo "  MQTT Broker: $MQTT_BROKER:$MQTT_PORT"
echo "  Device Name: $DEVICE_NAME"
echo "  Update Interval: ${UPDATE_INTERVAL}s"
echo ""
echo "To change settings:"
echo "  sudo nano $CONFIG_FILE"
echo "  sudo systemctl restart mqtt_publisher.service"
echo ""
echo "Next steps:"
echo "  1. Configure MQTT in Home Assistant (see docs/HOME_ASSISTANT_MQTT.md)"
echo "  2. Open port $MQTT_PORT on your router/firewall"
echo "  3. Forward port to Home Assistant"
echo ""
