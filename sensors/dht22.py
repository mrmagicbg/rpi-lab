#!/usr/bin/env python3
"""
DHT22 Temperature and Humidity Sensor Module
Reads temperature (°C) and humidity (%) from DHT22 sensor on GPIO pin.
"""

import logging
from typing import Optional, Tuple

try:
    import Adafruit_DHT
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False
    logging.warning("Adafruit_DHT library not available. DHT22 sensor will be disabled.")

# DHT22 sensor type
DHT_SENSOR = Adafruit_DHT.DHT22 if DHT_AVAILABLE else None

# Default GPIO pin for DHT22 data line (BCM numbering)
DEFAULT_DHT_PIN = 4  # GPIO4 (physical pin 7)


class DHT22Sensor:
    """DHT22 Temperature and Humidity Sensor interface."""
    
    def __init__(self, gpio_pin: int = DEFAULT_DHT_PIN):
        """
        Initialize DHT22 sensor.
        
        Args:
            gpio_pin: GPIO pin number (BCM numbering) where DHT22 data line is connected.
                     Default is GPIO4 (physical pin 7).
        """
        self.gpio_pin = gpio_pin
        self.available = DHT_AVAILABLE
        self.logger = logging.getLogger(__name__)
        
        if not self.available:
            self.logger.warning(f"DHT22 sensor disabled - Adafruit_DHT library not installed")
        else:
            self.logger.info(f"DHT22 sensor initialized on GPIO{gpio_pin}")
    
    def read(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Read temperature and humidity from DHT22 sensor.
        
        Returns:
            Tuple of (humidity, temperature) in (%, °C).
            Returns (None, None) if reading fails or sensor not available.
        """
        if not self.available:
            return None, None
        
        try:
            # Read from DHT22 sensor
            # Returns: (humidity, temperature) or (None, None) on error
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, self.gpio_pin)
            
            if humidity is not None and temperature is not None:
                self.logger.debug(f"DHT22 reading: {temperature:.1f}°C, {humidity:.1f}%")
                return humidity, temperature
            else:
                self.logger.warning("Failed to read from DHT22 sensor")
                return None, None
                
        except Exception as e:
            self.logger.error(f"Error reading DHT22 sensor: {e}")
            return None, None
    
    def read_formatted(self) -> Tuple[str, str]:
        """
        Read sensor and return formatted strings.
        
        Returns:
            Tuple of (temperature_str, humidity_str).
            Returns error messages if reading fails.
        """
        humidity, temperature = self.read()
        
        if temperature is not None and humidity is not None:
            temp_str = f"{temperature:.1f}°C"
            humid_str = f"{humidity:.1f}%"
        else:
            temp_str = "N/A"
            humid_str = "N/A"
        
        return temp_str, humid_str


def test_sensor(gpio_pin: int = DEFAULT_DHT_PIN):
    """Test DHT22 sensor reading (for debugging)."""
    import sys
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    sensor = DHT22Sensor(gpio_pin)
    
    if not sensor.available:
        print("ERROR: DHT22 sensor library not available")
        print("Install with: sudo pip3 install Adafruit_DHT")
        sys.exit(1)
    
    print(f"Reading from DHT22 sensor on GPIO{gpio_pin}...")
    humidity, temperature = sensor.read()
    
    if temperature is not None and humidity is not None:
        print(f"Temperature: {temperature:.1f}°C")
        print(f"Humidity: {humidity:.1f}%")
    else:
        print("Failed to read sensor. Check wiring and connections.")
        sys.exit(1)


if __name__ == "__main__":
    test_sensor()
