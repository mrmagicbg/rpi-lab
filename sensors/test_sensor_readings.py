#!/usr/bin/env python3
"""
Diagnostic script to test BME680/690 sensor readings
Shows raw values and expected ranges to identify calibration issues
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import bme680
    print("✓ bme680 library loaded")
except ImportError as e:
    print(f"✗ Failed to import bme680: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("BME680/690 Sensor Diagnostics")
print("=" * 70)

# Try to initialize sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    print(f"✓ Sensor initialized at address 0x{bme680.I2C_ADDR_PRIMARY:02X}")
except Exception as e:
    print(f"✗ Failed to initialize sensor at 0x76: {e}")
    try:
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        print(f"✓ Sensor initialized at address 0x{bme680.I2C_ADDR_SECONDARY:02X}")
    except Exception as e2:
        print(f"✗ Failed to initialize sensor at 0x77: {e2}")
        sys.exit(1)

# Configure sensor
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

print("\n" + "-" * 70)
print("Sensor Configuration:")
print("-" * 70)
print(f"Humidity oversample: OS_2X")
print(f"Pressure oversample: OS_4X")
print(f"Temperature oversample: OS_8X")
print(f"Filter: SIZE_3")
print(f"Gas heater: 320°C, 150ms")

# Take 3 readings
print("\n" + "-" * 70)
print("Taking 3 sensor readings...")
print("-" * 70)

readings = []
for i in range(3):
    if sensor.get_sensor_data():
        temp = sensor.data.temperature
        hum = sensor.data.humidity
        press = sensor.data.pressure
        gas = sensor.data.gas_resistance if hasattr(sensor.data, 'gas_resistance') else 0
        heat_stable = sensor.data.heat_stable if hasattr(sensor.data, 'heat_stable') else False
        
        readings.append({
            'temp': temp,
            'hum': hum,
            'press': press,
            'gas': gas,
            'heat_stable': heat_stable
        })
        
        print(f"\nReading {i+1}:")
        print(f"  Temperature:     {temp:.2f} °C")
        print(f"  Humidity:        {hum:.2f} %RH")
        print(f"  Pressure:        {press:.2f} hPa")
        print(f"  Gas Resistance:  {gas:.0f} Ω ({gas/1000:.1f} kΩ)")
        print(f"  Heat Stable:     {heat_stable}")
    else:
        print(f"\n✗ Reading {i+1} failed")
    
    if i < 2:
        import time
        time.sleep(1)

# Calculate averages
if readings:
    avg_temp = sum(r['temp'] for r in readings) / len(readings)
    avg_hum = sum(r['hum'] for r in readings) / len(readings)
    avg_press = sum(r['press'] for r in readings) / len(readings)
    avg_gas = sum(r['gas'] for r in readings) / len(readings)
    
    print("\n" + "=" * 70)
    print("Average Values:")
    print("=" * 70)
    print(f"Temperature:     {avg_temp:.2f} °C")
    print(f"Humidity:        {avg_hum:.2f} %RH")
    print(f"Pressure:        {avg_press:.2f} hPa")
    print(f"Gas Resistance:  {avg_gas:.0f} Ω ({avg_gas/1000:.1f} kΩ)")
    
    print("\n" + "=" * 70)
    print("Expected Ranges & Analysis:")
    print("=" * 70)
    
    # Temperature analysis
    print(f"\n🌡️  TEMPERATURE: {avg_temp:.1f}°C")
    if -40 <= avg_temp <= 85:
        if 0 <= avg_temp <= 40:
            print("   ✓ Normal indoor/outdoor range")
        else:
            print("   ⚠ Outside typical indoor range but within sensor spec")
    else:
        print("   ✗ Outside sensor specification (-40 to 85°C)")
    
    # Humidity analysis
    print(f"\n💧 HUMIDITY: {avg_hum:.1f}%RH")
    if 0 <= avg_hum <= 100:
        if 20 <= avg_hum <= 80:
            print("   ✓ Normal range")
        elif avg_hum < 20:
            print("   ⚠ Low (dry conditions)")
        else:
            print("   ⚠ High (humid conditions)")
    else:
        print("   ✗ INVALID - outside 0-100% range!")
    
    # Pressure analysis
    print(f"\n🌍 PRESSURE: {avg_press:.1f} hPa")
    if 950 <= avg_press <= 1050:
        print("   ✓ Normal atmospheric pressure")
    elif 300 <= avg_press <= 1100:
        print("   ⚠ Outside normal range but within sensor spec (300-1100 hPa)")
    else:
        print(f"   ✗ INVALID - outside sensor specification (300-1100 hPa)!")
        print(f"   ✗ Expected ~1013 hPa at sea level")
        print(f"   ✗ Your reading is {avg_press/1013:.1f}x too high")
        print("\n   Possible causes:")
        print("   - Sensor not properly calibrated")
        print("   - Hardware defect")
        print("   - Wrong sensor type (not BME680/690)")
    
    # Gas resistance analysis
    print(f"\n💨 GAS RESISTANCE: {avg_gas:.0f} Ω ({avg_gas/1000:.1f} kΩ)")
    if avg_gas < 5000:
        print("   ⚠ Very low - volatile gases detected")
    elif avg_gas < 10000:
        print("   ⚠ Low - sensor warming up")
    elif avg_gas < 50000:
        print("   ○ Moderate - stabilizing")
    elif avg_gas < 100000:
        print("   ✓ Good - stabilized")
    else:
        print("   ✓ Excellent - normal clean air")

print("\n" + "=" * 70)
print("Calibration Data:")
print("=" * 70)

# Try to read calibration coefficients if available
try:
    if hasattr(sensor, 'calibration_data'):
        cal = sensor.calibration_data
        print("Sensor has calibration data:")
        if hasattr(cal, 'par_p1'):
            print(f"  Pressure calibration present (par_p1: {cal.par_p1})")
        if hasattr(cal, 'par_t1'):
            print(f"  Temperature calibration present (par_t1: {cal.par_t1})")
        if hasattr(cal, 'par_h1'):
            print(f"  Humidity calibration present (par_h1: {cal.par_h1})")
    else:
        print("⚠ Cannot access calibration data")
except Exception as e:
    print(f"⚠ Error reading calibration: {e}")

print("\n" + "=" * 70)
