#!/usr/bin/env python3
"""
Check BME sensor chip ID and version
Helps identify BME280 vs BME680 vs BME688
"""

import sys
try:
    import smbus2
    import time
except ImportError:
    print("Error: smbus2 not installed")
    sys.exit(1)

# I2C addresses
PRIMARY_ADDR = 0x76
SECONDARY_ADDR = 0x77

# Register addresses
CHIP_ID_REG = 0xD0
VARIANT_ID_REG = 0xF0

# Known chip IDs
CHIP_IDS = {
    0x58: "BME280",
    0x60: "BME280",
    0x61: "BME680",
    0x88: "BME688"
}

print("=" * 70)
print("BME Sensor Chip Identification")
print("=" * 70)

bus = smbus2.SMBus(1)

for addr in [PRIMARY_ADDR, SECONDARY_ADDR]:
    try:
        print(f"\nTrying I2C address 0x{addr:02X}...")
        
        # Read chip ID
        chip_id = bus.read_byte_data(addr, CHIP_ID_REG)
        chip_name = CHIP_IDS.get(chip_id, f"Unknown (0x{chip_id:02X})")
        
        print(f"  ✓ Chip ID: 0x{chip_id:02X} = {chip_name}")
        
        # Try to read variant ID (BME688 only)
        try:
            variant_id = bus.read_byte_data(addr, VARIANT_ID_REG)
            print(f"  Variant ID: 0x{variant_id:02X}")
        except:
            pass
        
        if chip_id == 0x61:
            print(f"\n  ✓ This is a BME680 sensor")
            print(f"  ✓ Using bme680 Python library is correct")
            print(f"\n  ⚠ Pressure reading issue suggests:")
            print(f"     - Possible bug in bme680 library v2.0.0")
            print(f"     - Try downgrading: pip install bme680==1.1.1")
            
        elif chip_id == 0x88:
            print(f"\n  ✓ This is a BME688 sensor (newer version)")
            print(f"  ✓ Should work with bme680 library")
            
        elif chip_id in [0x58, 0x60]:
            print(f"\n  ✗ This is a BME280 sensor, NOT BME680/690!")
            print(f"  ✗ You need the BME280 library instead:")
            print(f"     pip uninstall bme680")
            print(f"     pip install pimoroni-bme280")
            print(f"  ✗ Code needs to import bme280, not bme680")
        
        break
        
    except Exception as e:
        print(f"  ✗ No sensor at 0x{addr:02X}: {e}")

bus.close()

print("\n" + "=" * 70)
print("Recommendation:")
print("=" * 70)
print("""
If BME680 with pressure bug:
  1. Try older library version:
     pip install bme680==1.1.1
  
  2. Or apply manual calibration in code:
     pressure_corrected = pressure_raw / 4.33
  
If BME280 detected:
  1. Install correct library:
     pip install pimoroni-bme280
  2. Update sensor code to use bme280 instead of bme680
""")
print("=" * 70)
