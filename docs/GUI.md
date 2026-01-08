# GUI Features

Touch-friendly GUI for Waveshare 4.3" 800×480 display.

## Overview

Full-screen GUI with:
- Real-time sensor data
- Network information
- System control buttons
- Color-coded gas status
- Audio alerts

## Layout

### Top Panel - Information Display

**Network Info (Left):**
- IP address with CIDR (e.g., 192.168.1.100/24)
- Gateway IP
- DNS servers (up to 2)
- Auto-updates every 30 seconds

**Sensor Data (Right):**
- Temperature (°C)
- Humidity (%RH)
- Pressure (hPa)
- Gas resistance (Ω) with status
- Auto-updates every 5 seconds

### Status Line

Shows:
- Last sensor update time
- Gas heater status (7 levels)

### Bottom Panel - Control Buttons

**5 Large Touch Buttons:**

1. **📡 TPMS Monitor** (Blue)
   - Launches tire pressure monitoring GUI
   - Requires CC1101 RF module

2. **🔊 Test Speaker** (Orange)
   - Plays test beep pattern
   - Verifies PWM speaker functionality

3. **🔄 Reboot System** (Red)
   - System reboot with confirmation dialog
   - Plays triple beep before reboot

4. **💻 Open Terminal** (Green)
   - Launches xterm window
   - For system administration

5. **❌ Exit Application** (Gray)
   - Closes GUI with confirmation
   - Returns to desktop

## Gas Heater Status

7 color-coded levels with resistance and emoji:

| Range | Status | Color | Emoji |
|-------|--------|-------|-------|
| < 5kΩ | Gas Detected | Red | ⚠️ |
| 5-10kΩ | Warm-Up | Orange | 🔥 |
| 10-20kΩ | Stabilizing | Yellow | ⏳ |
| 20-40kΩ | Cont. Stab. | Bright Yellow | 📈 |
| 40-60kΩ | Further Stab. | Light Green | 🔄 |
| 60-100kΩ | Stabilized | Green | ✅ |
| > 100kΩ | Normal | Bright Green | ✓ |

## Audio Alerts

### Alert Conditions

**Gas Detection:**
- Triggers: < 5kΩ (Red level only)
- Pattern: Double beep
- Interval: Every 15 seconds
- Purpose: Volatile gas warning

**Temperature:**
- Triggers: < 0°C or > 30°C
- Pattern: Triple beep
- Interval: Hourly
- Purpose: Extreme temperature warning

**Humidity:**
- Triggers: < 25% or > 80%
- Pattern: Double beep
- Interval: Hourly
- Purpose: Humidity out of range

**System Events:**
- Startup: Long beep
- Shutdown: Long beep
- Reboot: Triple beep

### Disabling Alerts

Set environment variable in service file:
```bash
Environment="SPEAKER_DRY_RUN=1"
```

## Keyboard Shortcuts

- **F11** - Toggle fullscreen
- **Escape** - Exit fullscreen
- **Ctrl+C** - Exit application (terminal only)

## Auto-Start

GUI starts automatically on boot via systemd service.

Manage:
```bash
sudo systemctl status rpi_gui.service
sudo systemctl restart rpi_gui.service
```

See [SERVICE_MANAGEMENT.md](SERVICE_MANAGEMENT.md) for details.

## Customization

Edit `/opt/rpi-lab/gui/rpi_gui.py`:

**Sensor thresholds:**
```python
self.temp_min = 0.0      # Minimum temperature (°C)
self.temp_max = 30.0     # Maximum temperature (°C)
self.humidity_min = 25.0 # Minimum humidity (%)
self.humidity_max = 80.0 # Maximum humidity (%)
self.gas_threshold = 5000 # Gas alert threshold (Ω)
```

**Update intervals:**
```python
self.network_update_interval = 30000  # Network (ms)
self.sensor_update_interval = 5000    # Sensor (ms)
```

After changes:
```bash
sudo systemctl restart rpi_gui.service
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for:
- GUI won't start
- Touch not responding
- Sensor shows "N/A"
- Network info missing
- Audio alerts not working
