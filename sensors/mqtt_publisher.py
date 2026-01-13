#!/usr/bin/env python3
"""
MQTT Publisher for BME690 Sensor Data to Home Assistant

Publishes temperature, humidity, pressure, and gas resistance data
to Home Assistant via MQTT with auto-discovery support.

Configuration:
  Edit config/sensor.conf [MQTT] section for broker settings.
  Environment variables used as fallback if config not found.
"""

import os
import sys
import time
import json
import logging
import signal
import configparser
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Error: paho-mqtt not installed. Run: pip install paho-mqtt")
    sys.exit(1)

# Add parent directory to path for sensor imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sensors.bme690 import BME690Sensor

# Config file paths (search in order)
CONFIG_PATHS = [
    "/opt/rpi-lab/config/sensor.conf",
    os.path.join(os.path.dirname(__file__), "..", "config", "sensor.conf"),
    os.path.expanduser("~/.config/rpi-lab/sensor.conf"),
]

def load_mqtt_config():
    """Load MQTT configuration from file or environment variables."""
    config = {
        'broker': 'homeassistant.local',
        'port': 1883,
        'username': '',
        'password': '',
        'topic_prefix': 'homeassistant',
        'device_name': 'rpi_lab',
        'update_interval': 60,
    }
    
    # Try to load from config file
    for config_path in CONFIG_PATHS:
        if os.path.exists(config_path):
            try:
                parser = configparser.ConfigParser()
                parser.read(config_path)
                
                if 'MQTT' in parser:
                    mqtt_section = parser['MQTT']
                    config['broker'] = mqtt_section.get('broker', config['broker'])
                    config['port'] = mqtt_section.getint('port', config['port'])
                    config['username'] = mqtt_section.get('username', config['username'])
                    config['password'] = mqtt_section.get('password', config['password'])
                    config['topic_prefix'] = mqtt_section.get('topic_prefix', config['topic_prefix'])
                    config['device_name'] = mqtt_section.get('device_name', config['device_name'])
                    config['update_interval'] = mqtt_section.getint('update_interval', config['update_interval'])
                    
                    logger.info(f"Loaded MQTT config from {config_path}")
                    return config
            except Exception as e:
                logger.warning(f"Failed to load MQTT config from {config_path}: {e}")
    
    # Fallback to environment variables
    config['broker'] = os.getenv('MQTT_BROKER', config['broker'])
    config['port'] = int(os.getenv('MQTT_PORT', str(config['port'])))
    config['username'] = os.getenv('MQTT_USER', config['username'])
    config['password'] = os.getenv('MQTT_PASSWORD', config['password'])
    config['topic_prefix'] = os.getenv('MQTT_TOPIC_PREFIX', config['topic_prefix'])
    config['device_name'] = os.getenv('DEVICE_NAME', config['device_name'])
    config['update_interval'] = int(os.getenv('UPDATE_INTERVAL', str(config['update_interval'])))
    
    logger.info("Using MQTT config from environment variables")
    return config

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mqtt_publisher')

# Load MQTT configuration
MQTT_CONFIG = load_mqtt_config()
MQTT_BROKER = MQTT_CONFIG['broker']
MQTT_PORT = MQTT_CONFIG['port']
MQTT_USER = MQTT_CONFIG['username']
MQTT_PASSWORD = MQTT_CONFIG['password']
MQTT_TOPIC_PREFIX = MQTT_CONFIG['topic_prefix']
DEVICE_NAME = MQTT_CONFIG['device_name']
UPDATE_INTERVAL = MQTT_CONFIG['update_interval']


class BME690Publisher:
    """Publishes BME690 sensor data to Home Assistant via MQTT."""
    
    def __init__(self):
        self.running = True
        self.sensor = None
        self.client = mqtt.Client(client_id=f"{DEVICE_NAME}_bme690")
        self.connected = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Setup callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        # Initialize sensor
        try:
            logger.info("Initializing BME690 sensor...")
            self.sensor = BME690Sensor()
            if not self.sensor.available:
                logger.error("BME690 sensor not available - check I2C connection")
                self.sensor = None
            else:
                logger.info("BME690 sensor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BME690 sensor: {e}")
            self.sensor = None
        
        # Setup authentication if provided
        if MQTT_USER and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
            logger.info("MQTT authentication configured")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to MQTT broker."""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            self.publish_discovery()
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from MQTT broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnect. Return code: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def on_message(self, client, userdata, msg):
        """Callback for received messages."""
        logger.debug(f"Received message on {msg.topic}: {msg.payload.decode()}")
    
    def publish_discovery(self):
        """Publish Home Assistant MQTT discovery configs."""
        device_info = {
            "identifiers": [f"{DEVICE_NAME}_bme690"],
            "name": "RPI Lab BME690",
            "model": "BME690",
            "manufacturer": "Bosch",
            "sw_version": "1.0.0"
        }
        
        sensors = [
            {
                "name": "temperature",
                "display_name": "RPI Lab Temperature",
                "unit": "°C",
                "device_class": "temperature",
                "state_class": "measurement",
                "icon": "mdi:thermometer"
            },
            {
                "name": "humidity",
                "display_name": "RPI Lab Humidity",
                "unit": "%",
                "device_class": "humidity",
                "state_class": "measurement",
                "icon": "mdi:water-percent"
            },
            {
                "name": "pressure",
                "display_name": "RPI Lab Pressure",
                "unit": "hPa",
                "device_class": "pressure",
                "state_class": "measurement",
                "icon": "mdi:gauge"
            },
            {
                "name": "gas_resistance",
                "display_name": "RPI Lab Gas Resistance",
                "unit": "kΩ",
                "device_class": None,
                "state_class": "measurement",
                "icon": "mdi:air-filter"
            }
        ]
        
        for sensor in sensors:
            config_topic = f"{MQTT_TOPIC_PREFIX}/sensor/{DEVICE_NAME}_{sensor['name']}/config"
            state_topic = f"{MQTT_TOPIC_PREFIX}/sensor/{DEVICE_NAME}/{sensor['name']}/state"
            
            config = {
                "name": sensor['display_name'],
                "state_topic": state_topic,
                "unit_of_measurement": sensor['unit'],
                "value_template": "{{ value_json.value }}",
                "unique_id": f"{DEVICE_NAME}_{sensor['name']}",
                "device": device_info,
                "icon": sensor['icon']
            }
            
            if sensor['device_class']:
                config["device_class"] = sensor['device_class']
            if sensor['state_class']:
                config["state_class"] = sensor['state_class']
            
            self.client.publish(config_topic, json.dumps(config), retain=True)
            logger.info(f"Published discovery config for {sensor['name']}")
    
    def publish_sensor_data(self):
        """Read sensor and publish data to MQTT."""
        if not self.sensor:
            logger.debug("Sensor not available")
            return
        
        try:
            h, t, p, g = self.sensor.read()
            
            if t is None:
                logger.debug("Sensor read returned None values")
                return
            
            timestamp = datetime.now().isoformat()
            
            # Scale gas resistance to kΩ for better readability in HA
            gas_kohm = round(g / 1000.0, 1) if g is not None else 0.0
            
            # Publish each sensor value
            sensors_data = {
                "temperature": {"value": round(t, 2), "timestamp": timestamp},
                "humidity": {"value": round(h, 2), "timestamp": timestamp},
                "pressure": {"value": round(p, 2), "timestamp": timestamp},
                "gas_resistance": {"value": gas_kohm, "timestamp": timestamp}
            }
            
            for sensor_name, data in sensors_data.items():
                topic = f"{MQTT_TOPIC_PREFIX}/sensor/{DEVICE_NAME}/{sensor_name}/state"
                payload = json.dumps(data)
                result = self.client.publish(topic, payload)
                
                if result.rc == 0:
                    logger.debug(f"Published {sensor_name}: {data['value']}")
                else:
                    logger.error(f"Failed to publish {sensor_name}")
            
            logger.info(f"Published: T={t:.1f}°C, H={h:.1f}%, P={p:.1f}hPa, G={gas_kohm:.1f}kΩ")
            
        except Exception as e:
            logger.error(f"Error reading/publishing sensor data: {e}")
    
    def connect(self):
        """Connect to MQTT broker with retry logic."""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} (attempt {attempt + 1}/{max_retries})")
                self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
                return True
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        logger.error("Failed to connect after all retries")
        return False
    
    def run(self):
        """Main loop - connect and publish sensor data periodically."""
        if not self.connect():
            logger.error("Could not connect to MQTT broker. Exiting.")
            return 1
        
        # Start network loop in background
        self.client.loop_start()
        
        # Wait for connection to establish
        for _ in range(10):
            if self.connected:
                break
            time.sleep(0.5)
        
        if not self.connected:
            logger.error("Failed to establish connection. Exiting.")
            return 1
        
        logger.info(f"Starting sensor publishing loop (interval: {UPDATE_INTERVAL}s)")
        
        try:
            while self.running:
                if self.connected:
                    self.publish_sensor_data()
                else:
                    logger.debug("Not connected to MQTT broker, waiting for reconnection...")
                
                time.sleep(UPDATE_INTERVAL)
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            return 1
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
        
        return 0


def main():
    """Entry point."""
    logger.info("=== BME690 MQTT Publisher Starting ===")
    logger.info(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    logger.info(f"Device Name: {DEVICE_NAME}")
    logger.info(f"Update Interval: {UPDATE_INTERVAL}s")
    
    publisher = BME690Publisher()
    return publisher.run()


if __name__ == '__main__':
    sys.exit(main())
