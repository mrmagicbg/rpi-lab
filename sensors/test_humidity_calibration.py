#!/usr/bin/env python3
"""
Test script for BME690 humidity calibration
Compares readings with different calibration settings
"""

import os
import sys
import time

# Test different configurations
configs = [
    {"desc": "Default (heater ON, no calibration)", "env": {}},
    {"desc": "Heater OFF (improved accuracy)", "env": {"BME690_ENABLE_GAS": "0"}},
    {"desc": "Heater ON + 15% offset", "env": {"BME690_HUM_OFFSET": "15.0"}},
    {"desc": "Heater ON + 20% offset", "env": {"BME690_HUM_OFFSET": "20.0"}},
    {"desc": "Heater OFF + 1.2x scale", "env": {"BME690_ENABLE_GAS": "0", "BME690_HUM_SCALE": "1.2"}},
]

print("=" * 70)
print("BME690 Humidity Calibration Test")
print("=" * 70)
print("\nThis script tests different calibration settings.")
print("Compare results to your reference humidity meter.\n")

for i, config in enumerate(configs, 1):
    print(f"\n[{i}/{len(configs)}] Testing: {config['desc']}")
    print("-" * 70)
    
    # Set environment variables for this test
    for key, value in config['env'].items():
        os.environ[key] = value
    
    # Remove any env vars not in this config
    for key in ['BME690_ENABLE_GAS', 'BME690_HUM_SCALE', 'BME690_HUM_OFFSET']:
        if key not in config['env']:
            os.environ.pop(key, None)
    
    # Import/reload the sensor module with new env vars
    if 'sensors.bme690' in sys.modules:
        del sys.modules['sensors.bme690']
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from sensors.bme690 import BME690Sensor
        
        sensor = BME690Sensor()
        if not sensor.available:
            print("❌ Sensor not available")
            continue
        
        # Take 3 readings and average
        readings = []
        for j in range(3):
            h, t, p, g = sensor.read()
            if h is not None:
                readings.append(h)
            time.sleep(0.5)
        
        if readings:
            avg_humidity = sum(readings) / len(readings)
            print(f"✓ Humidity readings: {readings}")
            print(f"✓ Average: {avg_humidity:.1f}%RH")
        else:
            print("❌ Failed to read sensor")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Clean up
    if 'sensors.bme690' in sys.modules:
        del sys.modules['sensors.bme690']

print("\n" + "=" * 70)
print("Test complete!")
print("\nRecommendations:")
print("1. Compare results to your reference meter")
print("2. Choose the configuration closest to the reference")
print("3. Set env vars in service files (see docs/TROUBLESHOOTING.md)")
print("=" * 70)
