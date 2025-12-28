# BME690 Wiring (Raspberry Pi 3)

This guide shows how to wire the Pimoroni BME690 breakout to a Raspberry Pi 3 via I2C.

## Pin Mapping

Use the 5-pin right-angle header to connect to the Pi GPIO header (pins 1, 3, 5, 7, 9). The essential connections are:

| BME690 | Raspberry Pi 3 | Function |
|--------|-----------------|----------|
| 3V3    | Pin 1          | Power (3.3V) |
| SDA    | Pin 3 (GPIO2)  | I2C Data |
| SCL    | Pin 5 (GPIO3)  | I2C Clock |
| GND    | Pin 9          | Ground |
| (NC)   | Pin 7 (GPIO4)  | Not used by BME690 |

### Physical Pin Layout Reference

```
   [USB]
    ___
   | 2 | 1   (3.3V)  ← BME690 3V3
   | 4 | 3   (SDA)    ← BME690 SDA
   | 6 | 5   (SCL)    ← BME690 SCL
   | 8 | 7   (GPIO4)  (not used)
   |10 | 9   (GND)    ← BME690 GND
   ...
```

## I2C Address

- Default I2C address: `0x76`
- Optional: Cut the `ADDR` trace on the back of the breakout to change the address to `0x77` if needed.
- Note: BME2xx/BME6xx devices share addresses; ensure unique addresses if using multiple.

## Enable I2C

Enable I2C on Raspberry Pi:

```bash
sudo raspi-config nonint do_i2c 0
sudo apt-get install -y i2c-tools
```

Verify the sensor appears on the bus:

```bash
sudo i2cdetect -y 1
# You should see 76 or 77 in the address grid
```

## References

- Pimoroni BME690 product page: https://shop.pimoroni.com/products/bme690-breakout
- Pimoroni Python library: https://github.com/pimoroni/bme690-python
- BME690 datasheet: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme690-ds001-00.pdf
