"""
Sensor modules for RPI Lab.

This package provides interfaces for various environmental sensors:
- BME690: Temperature, humidity, pressure, and gas resistance sensor
- MCP integration for remote sensor monitoring

Example:
    >>> from sensors.bme690 import BME690Sensor
    >>> sensor = BME690Sensor()
    >>> if sensor.available:
    ...     h, t, p, g = sensor.read()
    ...     print(f"Temperature: {t}°C, Humidity: {h}%")
"""

__version__ = "0.5.0"
__all__ = ["BME690Sensor", "BME690MCPTools"]

from .bme690 import BME690Sensor
from .bme690_mcp import BME690MCPTools
