#!/usr/bin/env python3
"""
BME690 MCP Server Tool Integration
Exposes BME690 sensor readings as MCP tools for remote monitoring via the MCP server.

This allows the main MCP server to query BME690 sensor data over HTTP.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

# Import the BME690 sensor module
from sensors.bme690 import BME690Sensor

logger = logging.getLogger(__name__)


class BME690MCPTools:
    """MCP tool wrappers for BME690 sensor."""

    def __init__(self):
        """Initialize sensor and tools."""
        self.sensor = BME690Sensor()

    def get_sensor_status(self) -> Dict[str, Any]:
        """Get BME690 sensor status and availability."""
        return {
            "available": self.sensor.available,
            "i2c_address": f"0x{self.sensor.i2c_addr:02X}" if self.sensor.i2c_addr else "unknown",
            "heat_stable": self.sensor.heat_stable,
            "dry_run": os.getenv("BME690_DRY_RUN", "0") == "1"
        }

    def read_all(self) -> Dict[str, Any]:
        """Read all BME690 sensor values."""
        if not self.sensor.available:
            return {
                "status": "error",
                "message": "BME690 sensor not available",
                "available": False
            }

        data = self.sensor.read_formatted()
        return {
            "status": "ok",
            "temperature": data["temperature_str"],
            "humidity": data["humidity_str"],
            "pressure": data["pressure_str"],
            "gas_resistance": data["gas_res_str"],
            "heat_stable": data["heat_stable"],
            "available": True
        }

    def read_temperature(self) -> Dict[str, Any]:
        """Read temperature only."""
        if not self.sensor.available:
            return {"status": "error", "message": "Sensor not available"}

        h, t, p, g = self.sensor.read()
        if t is None:
            return {"status": "error", "message": "Failed to read temperature"}

        return {
            "status": "ok",
            "temperature_celsius": round(float(t), 2),
            "temperature_fahrenheit": round((float(t) * 9 / 5) + 32, 2)
        }

    def read_humidity(self) -> Dict[str, Any]:
        """Read humidity only."""
        if not self.sensor.available:
            return {"status": "error", "message": "Sensor not available"}

        h, t, p, g = self.sensor.read()
        if h is None:
            return {"status": "error", "message": "Failed to read humidity"}

        return {
            "status": "ok",
            "humidity_percent": round(float(h), 2)
        }

    def read_pressure(self) -> Dict[str, Any]:
        """Read pressure and calculate altitude."""
        if not self.sensor.available:
            return {"status": "error", "message": "Sensor not available"}

        h, t, p, g = self.sensor.read()
        if p is None:
            return {"status": "error", "message": "Failed to read pressure"}

        p_val = float(p)
        # Sea level reference pressure
        P0 = 1013.25

        # Barometric formula: altitude = 44330 * (1 - (P/P0)^(1/5.255))
        altitude = 44330 * (1.0 - pow(p_val / P0, 1.0 / 5.255))

        return {
            "status": "ok",
            "pressure_hpa": round(p_val, 2),
            "altitude_meters": round(altitude, 1)
        }

    def read_gas_resistance(self) -> Dict[str, Any]:
        """Read gas resistance (air quality indicator)."""
        if not self.sensor.available:
            return {"status": "error", "message": "Sensor not available"}

        h, t, p, g = self.sensor.read()
        if g is None or g <= 0:
            return {"status": "error", "message": "Gas sensor not ready"}

        g_val = float(g)
        # Simple IAQ approximation (lower resistance = worse air quality)
        # This is a simplified version; Bosch provides more complex algorithms
        if g_val > 100000:
            air_quality = "Good"
        elif g_val > 50000:
            air_quality = "Moderate"
        elif g_val > 10000:
            air_quality = "Poor"
        else:
            air_quality = "Very Poor"

        return {
            "status": "ok",
            "gas_resistance_ohms": round(g_val, 0),
            "air_quality_estimate": air_quality
        }


def main():
    """Test MCP tools."""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    tools = BME690MCPTools()

    print("BME690 MCP Tools Test")
    print("=" * 60)
    print()

    print("Sensor Status:")
    print(json.dumps(tools.get_sensor_status(), indent=2))
    print()

    print("All Sensor Readings:")
    print(json.dumps(tools.read_all(), indent=2))
    print()

    print("Temperature:")
    print(json.dumps(tools.read_temperature(), indent=2))
    print()

    print("Humidity:")
    print(json.dumps(tools.read_humidity(), indent=2))
    print()

    print("Pressure & Altitude:")
    print(json.dumps(tools.read_pressure(), indent=2))
    print()

    print("Gas Resistance & Air Quality:")
    print(json.dumps(tools.read_gas_resistance(), indent=2))


if __name__ == "__main__":
    main()
