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

# 1. Install paho-mqtt in virtual environment
echo "Step 1: Installing paho-mqtt Python library..."
if [ -f "$PROJECT_ROOT/.venv/bin/pip" ]; then
    "$PROJECT_ROOT/.venv/bin/pip" install paho-mqtt
    echo "✓ paho-mqtt installed"
else
    echo "Error: Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "Run venv_setup.sh first"
    exit 1
fi

# 2. Make mqtt_publisher.py executable
echo "Step 2: Making mqtt_publisher.py executable..."
chmod +x "$PROJECT_ROOT/sensors/mqtt_publisher.py"
echo "✓ mqtt_publisher.py is executable"

# 3. Configure service file
echo "Step 3: Configuring systemd service..."

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

# Create configured service file
SERVICE_FILE="/etc/systemd/system/mqtt_publisher.service"
cp "$PROJECT_ROOT/sensors/mqtt_publisher.service" "$SERVICE_FILE"

# Update service file with user configuration
sed -i "s|Environment=\"MQTT_BROKER=.*\"|Environment=\"MQTT_BROKER=$MQTT_BROKER\"|" "$SERVICE_FILE"
sed -i "s|Environment=\"MQTT_PORT=.*\"|Environment=\"MQTT_PORT=$MQTT_PORT\"|" "$SERVICE_FILE"
sed -i "s|Environment=\"MQTT_USER=.*\"|Environment=\"MQTT_USER=$MQTT_USER\"|" "$SERVICE_FILE"
sed -i "s|Environment=\"MQTT_PASSWORD=.*\"|Environment=\"MQTT_PASSWORD=$MQTT_PASSWORD\"|" "$SERVICE_FILE"
sed -i "s|Environment=\"DEVICE_NAME=.*\"|Environment=\"DEVICE_NAME=$DEVICE_NAME\"|" "$SERVICE_FILE"
sed -i "s|Environment=\"UPDATE_INTERVAL=.*\"|Environment=\"UPDATE_INTERVAL=$UPDATE_INTERVAL\"|" "$SERVICE_FILE"

# Update user if not mrmagic
CURRENT_USER=$(logname 2>/dev/null || echo "$SUDO_USER")
if [ -n "$CURRENT_USER" ] && [ "$CURRENT_USER" != "mrmagic" ]; then
    sed -i "s|User=mrmagic|User=$CURRENT_USER|" "$SERVICE_FILE"
    echo "✓ Service configured for user: $CURRENT_USER"
fi

echo "✓ Service file created: $SERVICE_FILE"

# 4. Enable and start service
echo "Step 4: Enabling and starting service..."
systemctl daemon-reload
systemctl enable mqtt_publisher.service
systemctl start mqtt_publisher.service

echo "✓ Service enabled and started"

# 5. Show status
echo ""
echo "=== Installation Complete ==="
echo ""
echo "Service status:"
systemctl status mqtt_publisher.service --no-pager -l | head -20
echo ""
echo "View logs with:"
echo "  sudo journalctl -u mqtt_publisher.service -f"
echo ""
echo "Configuration:"
echo "  MQTT Broker: $MQTT_BROKER:$MQTT_PORT"
echo "  Device Name: $DEVICE_NAME"
echo "  Update Interval: ${UPDATE_INTERVAL}s"
echo ""
echo "Next steps:"
echo "  1. Configure MQTT in Home Assistant (see docs/HOME_ASSISTANT_MQTT.md)"
echo "  2. Open port $MQTT_PORT on your router/firewall"
echo "  3. Forward port to Home Assistant"
echo ""
