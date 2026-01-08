# TUI (Text User Interface) - SSH Monitoring

Monitor sensor data remotely via SSH using the rich-based TUI interface.

## Quick Start with Aliases

The easiest way to access the TUI is via bash aliases. These are **automatically created** during installation, but you can set them up manually:

### Auto-Install (Already Done)

During deployment, aliases are created in `~/.bash_aliases`:

```bash
alias rpi-tui='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py'
alias rpi-tui-sensor='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --sensor'
alias rpi-tui-rf='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --rf'
```

### Manual Setup (If Needed)

To create the aliases manually:

```bash
# SSH into your Pi
ssh user@raspberry-pi-ip

# Add aliases to ~/.bash_aliases
echo "# RPI Lab TUI aliases" >> ~/.bash_aliases
echo "alias rpi-tui='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py'" >> ~/.bash_aliases
echo "alias rpi-tui-sensor='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --sensor'" >> ~/.bash_aliases
echo "alias rpi-tui-rf='/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --rf'" >> ~/.bash_aliases

# Reload for current session
source ~/.bash_aliases
```

## Using the TUI

### Quick Commands

```bash
# SSH into Pi
ssh user@raspberry-pi-ip

# Full TUI (both sensor and RF panels)
rpi-tui

# Sensor data only
rpi-tui-sensor

# RF/TPMS data only
rpi-tui-rf

# Custom refresh interval
rpi-tui --interval 1.0
rpi-tui-sensor --interval 0.5

# Press Ctrl+C to exit
```

### Full Commands (Without Aliases)

```bash
# Monitor sensor data (default)
/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py

# Monitor with custom interval
/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --interval 5.0

# Show RF/TPMS data only
/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --rf

# Show both panels
/opt/rpi-lab/.venv/bin/python /opt/rpi-lab/gui/rpi_tui.py --both
```

## Features

### Real-time Sensor Display
- Temperature (°C), humidity (%RH), pressure (hPa)
- Gas resistance (Ω) with heater status
- Last update time

### Color-coded Gas Status (7 Levels)

| Status | Range | Color | Emoji |
|--------|-------|-------|-------|
| Gas Detected | < 5kΩ | Red | ⚠️ |
| Initial Warm-Up | 5-10kΩ | Orange | 🔥 |
| Stabilizing | 10-20kΩ | Yellow | ⏳ |
| Continued Stab. | 20-40kΩ | Bright Yellow | 📈 |
| Further Stab. | 40-60kΩ | Light Green | 🔄 |
| Stabilized | 60-100kΩ | Green | ✅ |
| Normal Operation | > 100kΩ | Bright Green | ✓ |

### RF/TPMS Monitoring
- View detected tire pressure sensors
- Sensor IDs and data packets

### Performance
- **Minimal Overhead**: Lightweight terminal-based interface
- **Auto-refresh**: Configurable update interval (default: 2 seconds)
- **Perfect for**: SSH monitoring, headless systems, remote debugging

## Requirements

- SSH access to Raspberry Pi
- Terminal with color support (99% of modern terminals)
- Already included: `rich` library in requirements.txt

## Troubleshooting

### Aliases not found
```bash
# Reload shell configuration
source ~/.bash_aliases

# Or restart SSH session
exit
ssh user@raspberry-pi-ip
```

### Sensor data not updating
```bash
# Check BME690 sensor status
i2cdetect -y 1

# Check service logs
journalctl -u rpi_gui.service -f
```

### Terminal colors not displaying
- Ensure terminal supports 256 colors: `echo $TERM`
- Try: `export TERM=xterm-256color`

### Permission denied
```bash
# Ensure .venv has read permissions
ls -la /opt/rpi-lab/.venv/bin/python

# Regenerate if needed
sudo /opt/rpi-lab/install/venv_setup.sh
```
