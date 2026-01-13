#!/usr/bin/env python3
"""
BME690 Environmental Sensor Module
Reads temperature (°C), humidity (%RH), pressure (hPa) and gas resistance (Ohms)
from Pimoroni BME690 breakout over I2C.

Configuration:
  Edit config/sensor.conf to set calibration values and heater control.
  Config file takes precedence over environment variables.

Environment Variables (fallback if config file not found):
  BME690_DRY_RUN=1        : Enable dry-run mode (simulated values, no hardware)
  BME690_ENABLE_GAS=0     : Disable gas heater (improves humidity accuracy)
  BME690_HUM_SCALE=1.0    : Humidity scaling factor (default: 1.0)
  BME690_HUM_OFFSET=0.0   : Humidity offset in %RH (default: 0.0)

Humidity Calibration:
  The gas heater on BME690/BME688 can cause lower humidity readings. If readings
  are consistently below a reference meter, disable the heater or apply calibration.
  See config/sensor.conf for details.
"""

import os
import time
import logging
import configparser
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Config file paths (search in order)
CONFIG_PATHS = [
    "/opt/rpi-lab/config/sensor.conf",
    os.path.join(os.path.dirname(__file__), "..", "config", "sensor.conf"),
    os.path.expanduser("~/.config/rpi-lab/sensor.conf"),
]

def load_sensor_config() -> Dict[str, Any]:
    """Load sensor configuration from file or environment variables."""
    config = {
        'dry_run': False,
        'enable_gas': True,
        'humidity_scale': 1.0,
        'humidity_offset': 0.0,
        'temperature_offset': 0.0,
        'pressure_correction': 4.33,
    }
    
    # Try to load from config file
    config_loaded = False
    for config_path in CONFIG_PATHS:
        if os.path.exists(config_path):
            try:
                parser = configparser.ConfigParser()
                parser.read(config_path)
                
                if 'BME690' in parser:
                    bme_section = parser['BME690']
                    config['dry_run'] = bme_section.getboolean('dry_run', False)
                    config['enable_gas'] = bme_section.getboolean('enable_gas', True)
                    config['humidity_scale'] = bme_section.getfloat('humidity_scale', 1.0)
                    config['humidity_offset'] = bme_section.getfloat('humidity_offset', 0.0)
                    config['temperature_offset'] = bme_section.getfloat('temperature_offset', 0.0)
                    config['pressure_correction'] = bme_section.getfloat('pressure_correction', 4.33)
                    
                    logger.info(f"Loaded sensor config from {config_path}")
                    config_loaded = True
                    break
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
    
    # Fallback to environment variables
    if not config_loaded:
        config['dry_run'] = os.getenv("BME690_DRY_RUN", "0") == "1"
        config['enable_gas'] = os.getenv("BME690_ENABLE_GAS", "1") == "1"
        config['humidity_scale'] = float(os.getenv("BME690_HUM_SCALE", "1.0"))
        config['humidity_offset'] = float(os.getenv("BME690_HUM_OFFSET", "0.0"))
        config['temperature_offset'] = float(os.getenv("BME690_TEMP_OFFSET", "0.0"))
        logger.info("Using sensor config from environment variables")
    
    return config

# Load configuration
SENSOR_CONFIG = load_sensor_config()
DRY_RUN = SENSOR_CONFIG['dry_run']
BME690_ENABLE_GAS = SENSOR_CONFIG['enable_gas']
HUM_SCALE = SENSOR_CONFIG['humidity_scale']
HUM_OFFSET = SENSOR_CONFIG['humidity_offset']
TEMP_OFFSET = SENSOR_CONFIG['temperature_offset']
PRESSURE_CORRECTION = SENSOR_CONFIG['pressure_correction']

try:
    import bme680
    LIB_AVAILABLE = True
except ImportError:
    LIB_AVAILABLE = False
    logger.warning("bme680 library not available. Sensor will use dry-run if enabled.")


class BME690Sensor:
    """BME690 Environmental Sensor interface."""

    def __init__(self, i2c_addr: Optional[int] = None):
        """
        Initialize BME690 sensor.

        Args:
            i2c_addr: I2C address (0x76 primary or 0x77 secondary). If None,
                      attempts primary then secondary.
        """
        self.available = False
        self.heat_stable = False
        self.i2c_addr = i2c_addr

        if DRY_RUN:
            logger.info("BME690 dry-run mode enabled (no hardware required)")
            self.available = True
            return

        if not LIB_AVAILABLE:
            logger.error("bme680 library not installed (pip install bme680)")
            return

        try:
            if i2c_addr is None:
                try:
                    self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
                    self.i2c_addr = bme680.I2C_ADDR_PRIMARY
                except (RuntimeError, IOError):
                    self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
                    self.i2c_addr = bme680.I2C_ADDR_SECONDARY
            else:
                self.sensor = bme680.BME680(i2c_addr)

            # Configure oversampling and filter
            self.sensor.set_humidity_oversample(bme680.OS_2X)
            self.sensor.set_pressure_oversample(bme680.OS_4X)
            self.sensor.set_temperature_oversample(bme680.OS_8X)
            self.sensor.set_filter(bme680.FILTER_SIZE_3)

            # Gas measurement / heater profile (can be disabled via env)
            if BME690_ENABLE_GAS:
                self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
                self.sensor.set_gas_heater_temperature(320)
                self.sensor.set_gas_heater_duration(150)
                self.sensor.select_gas_heater_profile(0)
                logger.info("BME690 gas heater enabled (320°C, 150ms)")
            else:
                # Disable gas heater to avoid lowering humidity readings
                self.sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
                logger.info("BME690 gas heater disabled (improves humidity accuracy)")

            self.available = True
            logger.info(f"BME690 initialized on I2C address 0x{self.i2c_addr:02X}")
            if HUM_SCALE != 1.0 or HUM_OFFSET != 0.0:
                logger.info(f"Humidity calibration: scale={HUM_SCALE}, offset={HUM_OFFSET}%RH")
            if TEMP_OFFSET != 0.0:
                logger.info(f"Temperature calibration: offset={TEMP_OFFSET}°C")
            if PRESSURE_CORRECTION != 4.33:
                logger.info(f"Pressure correction: factor={PRESSURE_CORRECTION}")
        except Exception as e:
            logger.error(f"Failed to initialize BME690: {e}")
            self.available = False

    def read(self, max_retries: int = 3, retry_delay: float = 0.1) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Read humidity (%), temperature (°C), pressure (hPa), gas resistance (Ohms).
        
        Implements exponential backoff retry for transient I2C errors.

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Initial delay between retries in seconds (default: 0.1s)

        Returns:
            Tuple (humidity, temperature, pressure, gas_resistance). Returns
            Nones if reading fails after all retries or sensor not available.
        """
        if not self.available:
            return None, None, None, None

        if DRY_RUN:
            # Simulated values for development/testing
            t = 22.5
            h = 45.0
            p = 1013.25
            g = 10000.0
            return h, t, p, g

        # Retry loop with exponential backoff for transient I2C errors
        for attempt in range(max_retries):
            try:
                if self.sensor.get_sensor_data():
                    self.heat_stable = bool(getattr(self.sensor.data, "heat_stable", False))
                    raw_temperature = float(self.sensor.data.temperature)
                    temperature = raw_temperature + TEMP_OFFSET
                    
                    # BUGFIX: bme680 library v2.0.0 with BME688 chip (BME690 breakout)
                    # Pressure reads 4.33x too high - apply correction factor
                    pressure_raw = float(self.sensor.data.pressure)
                    pressure = pressure_raw / PRESSURE_CORRECTION
                    
                    raw_humidity = float(self.sensor.data.humidity)
                    gas_resistance = float(getattr(self.sensor.data, "gas_resistance", 0.0))

                    # Apply optional humidity calibration and clamp to 0..100
                    humidity = max(0.0, min(100.0, raw_humidity * HUM_SCALE + HUM_OFFSET))
                    
                    # Log calibration application if active (debug level)
                    if (HUM_SCALE != 1.0 or HUM_OFFSET != 0.0) and raw_humidity != humidity:
                        logger.debug(f"Humidity calibrated: {raw_humidity:.1f}%RH → {humidity:.1f}%RH")
                    if TEMP_OFFSET != 0.0:
                        logger.debug(f"Temperature calibrated: {raw_temperature:.1f}°C → {temperature:.1f}°C")
                    
                    # Success - log if it took retries
                    if attempt > 0:
                        logger.info(f"BME690 read succeeded after {attempt + 1} attempts")
                    
                    return humidity, temperature, pressure, gas_resistance
                else:
                    # No data available, but no exception - might be sensor warming up
                    if attempt < max_retries - 1:
                        logger.debug(f"BME690 no data on attempt {attempt + 1}, retrying...")
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        logger.warning("BME690 no data after all retry attempts")
                        return None, None, None, None
                        
            except (OSError, IOError) as e:
                # I2C bus errors - these are often transient
                if attempt < max_retries - 1:
                    logger.debug(f"I2C error on attempt {attempt + 1}: {e}, retrying...")
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    logger.error(f"I2C error reading BME690 after {max_retries} attempts: {e}")
                    return None, None, None, None
                    
            except Exception as e:
                # Unexpected errors - log and retry
                if attempt < max_retries - 1:
                    logger.debug(f"Error on attempt {attempt + 1}: {e}, retrying...")
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    logger.error(f"Error reading BME690 after {max_retries} attempts: {e}")
                    return None, None, None, None
        
        # Should not reach here, but safety fallback
        return None, None, None, None

    def read_formatted(self) -> Dict[str, Any]:
        """
        Read sensor and return formatted values and status.

        Returns dict with keys:
            temperature_str, humidity_str, pressure_str, gas_res_str, heat_stable
        """
        h, t, p, g = self.read()

        fmt = {
            "temperature_str": "N/A",
            "humidity_str": "N/A",
            "pressure_str": "N/A",
            "gas_res_str": "N/A",
            "heat_stable": self.heat_stable,
        }

        if t is not None:
            fmt["temperature_str"] = f"{t:.2f}°C"
        if h is not None:
            fmt["humidity_str"] = f"{h:.2f}%"
        if p is not None:
            fmt["pressure_str"] = f"{p:.2f} hPa"
        if g is not None and g > 0:
            fmt["gas_res_str"] = f"{g:.0f} Ω"

        return fmt


def test_sensor():
    """Test BME690 sensor reading (for debugging)."""
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    sensor = BME690Sensor()
    if not sensor.available:
        print("ERROR: BME690 sensor not available")
        if not LIB_AVAILABLE:
            print("Install with: pip install bme690")
        print("Ensure I2C is enabled: sudo raspi-config nonint do_i2c 0")
        sys.exit(1)

    print("Reading from BME690 sensor...")
    data = sensor.read_formatted()
    print(f"Temperature: {data['temperature_str']}")
    print(f"Humidity: {data['humidity_str']}")
    print(f"Pressure: {data['pressure_str']}")
    print(f"Gas Resistance: {data['gas_res_str']}")
    print(f"Heater Stable: {'Yes' if data['heat_stable'] else 'No'}")


if __name__ == "__main__":
    test_sensor()
