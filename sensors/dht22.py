#!/usr/bin/env python3
"""
DHT22 Temperature and Humidity Sensor Module
Reads temperature (°C) and humidity (%) from DHT22 sensor on GPIO pin.
"""

import logging
import time
from typing import Optional, Tuple

try:
    from gpiozero import MCP3008, Device
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    # Try to set up gpiozero with RPi GPIO backend
    try:
        Device.pin_factory = RPiGPIOFactory()
    except:
        pass
    
    # For DHT22, we'll use a pure Python implementation with gpiozero/RPi.GPIO
    import RPi.GPIO as GPIO
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False
    logging.warning("gpiozero library not available. DHT22 sensor will be disabled.")

# Default GPIO pin for DHT22 data line (BCM numbering)
DEFAULT_DHT_PIN = 4  # GPIO4 (physical pin 7)


class DHT22Sensor:
    """DHT22 Temperature and Humidity Sensor interface."""
    
    MAX_TIMINGS = 100
    
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
            self.logger.warning(f"DHT22 sensor disabled - gpiozero/RPi.GPIO library not installed")
        else:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(gpio_pin, GPIO.OUT)
                self.logger.info(f"DHT22 sensor initialized on GPIO{gpio_pin}")
            except Exception as e:
                self.logger.error(f"Failed to initialize DHT22 sensor: {e}")
                self.available = False
    
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
            # Send start signal
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            GPIO.output(self.gpio_pin, GPIO.LOW)
            time.sleep(0.02)  # 20ms low pulse
            GPIO.output(self.gpio_pin, GPIO.HIGH)
            
            # Read sensor response
            GPIO.setup(self.gpio_pin, GPIO.IN)
            
            # Wait for sensor to pull low
            counter = 0
            while GPIO.input(self.gpio_pin) == GPIO.HIGH and counter < self.MAX_TIMINGS:
                counter += 1
                time.sleep(0.00001)
            
            if counter >= self.MAX_TIMINGS:
                self.logger.warning("DHT22 sensor timeout (no response)")
                return None, None
            
            # Read 40 bits of data
            bits = []
            for i in range(40):
                counter = 0
                while GPIO.input(self.gpio_pin) == GPIO.LOW and counter < self.MAX_TIMINGS:
                    counter += 1
                    time.sleep(0.00001)
                
                low_time = counter
                counter = 0
                while GPIO.input(self.gpio_pin) == GPIO.HIGH and counter < self.MAX_TIMINGS:
                    counter += 1
                    time.sleep(0.00001)
                
                high_time = counter
                
                # High pulse > 50us = 1, else 0
                if high_time > low_time:
                    bits.append(1)
                else:
                    bits.append(0)
            
            # Convert bits to bytes
            humidity_int = (bits[0] << 7) + (bits[1] << 6) + (bits[2] << 5) + (bits[3] << 4) + \
                          (bits[4] << 3) + (bits[5] << 2) + (bits[6] << 1) + bits[7]
            humidity_dec = (bits[8] << 7) + (bits[9] << 6) + (bits[10] << 5) + (bits[11] << 4) + \
                          (bits[12] << 3) + (bits[13] << 2) + (bits[14] << 1) + bits[15]
            
            temp_int = (bits[16] << 7) + (bits[17] << 6) + (bits[18] << 5) + (bits[19] << 4) + \
                      (bits[20] << 3) + (bits[21] << 2) + (bits[22] << 1) + bits[23]
            temp_dec = (bits[24] << 7) + (bits[25] << 6) + (bits[26] << 5) + (bits[27] << 4) + \
                      (bits[28] << 3) + (bits[29] << 2) + (bits[30] << 1) + bits[31]
            
            checksum = (bits[32] << 7) + (bits[33] << 6) + (bits[34] << 5) + (bits[35] << 4) + \
                      (bits[36] << 3) + (bits[37] << 2) + (bits[38] << 1) + bits[39]
            
            # Check checksum
            check = (humidity_int + humidity_dec + temp_int + temp_dec) & 0xFF
            if check != checksum:
                self.logger.warning("DHT22 checksum failed")
                return None, None
            
            humidity = (humidity_int + humidity_dec / 100.0)
            temperature = (temp_int + temp_dec / 100.0)
            
            self.logger.debug(f"DHT22 reading: {temperature:.1f}°C, {humidity:.1f}%")
            return humidity, temperature
                
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
        print("Install with: pip install gpiozero")
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
