#!/usr/bin/env python3
"""
BME690 Environmental Sensor Module
Reads temperature (°C), humidity (%RH), pressure (hPa) and gas resistance (Ohms)
from Pimoroni BME690 breakout over I2C.

Supports dry-run mode for development without hardware by setting the
environment variable BME690_DRY_RUN=1.
"""

import os
import time
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

DRY_RUN = os.getenv("BME690_DRY_RUN", "0") == "1"

try:
    import bme690
    LIB_AVAILABLE = True
except ImportError:
    LIB_AVAILABLE = False
    logger.warning("bme690 library not available. Sensor will use dry-run if enabled.")


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
            logger.error("bme690 library not installed")
            return

        try:
            if i2c_addr is None:
                try:
                    self.sensor = bme690.BME690(bme690.I2C_ADDR_PRIMARY)
                    self.i2c_addr = bme690.I2C_ADDR_PRIMARY
                except (RuntimeError, IOError):
                    self.sensor = bme690.BME690(bme690.I2C_ADDR_SECONDARY)
                    self.i2c_addr = bme690.I2C_ADDR_SECONDARY
            else:
                self.sensor = bme690.BME690(i2c_addr)

            # Configure oversampling and filter
            self.sensor.set_humidity_oversample(bme690.OS_2X)
            self.sensor.set_pressure_oversample(bme690.OS_4X)
            self.sensor.set_temperature_oversample(bme690.OS_8X)
            self.sensor.set_filter(bme690.FILTER_SIZE_3)

            # Enable gas measurement and set heater profile
            self.sensor.set_gas_status(bme690.ENABLE_GAS_MEAS)
            self.sensor.set_gas_heater_temperature(320)
            self.sensor.set_gas_heater_duration(150)
            self.sensor.select_gas_heater_profile(0)

            self.available = True
            logger.info(f"BME690 initialized on I2C address 0x{self.i2c_addr:02X}")
        except Exception as e:
            logger.error(f"Failed to initialize BME690: {e}")
            self.available = False

    def read(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        Read humidity (%), temperature (°C), pressure (hPa), gas resistance (Ohms).

        Returns:
            Tuple (humidity, temperature, pressure, gas_resistance). Returns
            Nones if reading fails or sensor not available.
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

        try:
            if self.sensor.get_sensor_data():
                self.heat_stable = bool(getattr(self.sensor.data, "heat_stable", False))
                temperature = float(self.sensor.data.temperature)
                pressure = float(self.sensor.data.pressure)
                humidity = float(self.sensor.data.humidity)
                gas_resistance = float(getattr(self.sensor.data, "gas_resistance", 0.0))
                return humidity, temperature, pressure, gas_resistance
            else:
                return None, None, None, None
        except Exception as e:
            logger.error(f"Error reading BME690: {e}")
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
