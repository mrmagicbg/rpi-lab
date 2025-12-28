# BME690 Setup (Raspberry Pi 3)

This guide covers installing and testing the Pimoroni BME690 Python library with this project.

## Prerequisites

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip rsync i2c-tools python3-smbus
sudo raspi-config nonint do_i2c 0  # enable I2C
```

## Install Project

```bash
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/install_gui.sh
sudo reboot
```

## Python Dependencies

The project uses the `bme690` PyPI package:

```bash
source /opt/rpi-lab/.venv/bin/activate
pip install bme690 smbus2
```

Alternatively, use Pimoroni's install script for the library:

```bash
git clone https://github.com/pimoroni/bme690-python
cd bme690-python
./install.sh
```

## Test the Sensor

This project supports a dry-run mode for development without hardware.

### Dry-Run (no hardware)

```bash
source /opt/rpi-lab/.venv/bin/activate
export BME690_DRY_RUN=1
python3 -m sensors.bme690
```

### Hardware Test

```bash
source /opt/rpi-lab/.venv/bin/activate
unset BME690_DRY_RUN
python3 -m sensors.bme690
```

You should see formatted readings for temperature, humidity, pressure and gas resistance.

## GUI Autostart

The GUI auto-starts fullscreen on boot via a systemd service:

- Service file: `gui/rpi_gui.service`
- Runs: `/opt/rpi-lab/gui/rpi_gui.py`
- Includes `SupplementaryGroups=i2c` for I2C access

Manage the service:

```bash
sudo systemctl status rpi_gui.service
sudo journalctl -u rpi_gui.service -f
sudo systemctl restart rpi_gui.service
```

## Troubleshooting

- Run `sudo i2cdetect -y 1` to confirm the sensor is detected at `0x76` or `0x77`.
- Ensure your user is in the `i2c` group: `sudo usermod -a -G i2c mrmagic`.
- If readings are `N/A`, check wiring and that I2C is enabled.
