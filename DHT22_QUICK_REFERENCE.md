# RPI Lab DHT22 Quick Reference Card

## Wiring (30 seconds)

```
DHT22           Raspberry Pi
────────────────────────────
VCC (Pin 1) →   Pin 1 (3.3V)
DATA (Pin 2) →  Pin 7 (GPIO4)
GND (Pin 4) →   Pin 6 (GND)
```

## Installation (5 minutes)

```bash
git clone https://github.com/mrmagicbg/rpi-lab.git ~/rpi-lab
sudo rsync -a --chown=root:root ~/rpi-lab/ /opt/rpi-lab/
sudo /opt/rpi-lab/install/venv_setup.sh
sudo /opt/rpi-lab/install/install_gui.sh
sudo reboot
```

## Test Sensor

```bash
cd /opt/rpi-lab
source .venv/bin/activate
python3 -m sensors.dht22
```

Expected: `Temperature: XX.X°C` and `Humidity: YY.Y%`

## Common Commands

| Task | Command |
|------|---------|
| Start GUI | `sudo systemctl start rpi_gui.service` |
| Stop GUI | `sudo systemctl stop rpi_gui.service` |
| Check status | `sudo systemctl status rpi_gui.service` |
| View logs | `sudo journalctl -u rpi_gui.service -f` |
| Test sensor | `cd /opt/rpi-lab && source .venv/bin/activate && python3 -m sensors.dht22` |
| Enable auto-start | `sudo systemctl enable rpi_gui.service` |
| Disable auto-start | `sudo systemctl disable rpi_gui.service` |

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "N/A" readings | Check wiring (VCC=3.3V, GND=0V, GPIO4 connected) |
| "checksum failed" | Add 4.7kΩ resistor between VCC and DATA |
| Permission denied | `sudo usermod -a -G gpio $USER && logout` |
| Service won't start | Check logs: `sudo journalctl -u rpi_gui.service -n 50` |
| Sensor timeout | Move away from electrical interference, shorten wires |

## Files Modified

✅ `sensors/dht22.py` - Modern DHT22 implementation  
✅ `requirements.txt` - Updated dependencies  
✅ `install/venv_setup.sh` - Simplified setup  
✅ `install/install_gui.sh` - Added GPIO group  
✅ `gui/rpi_gui.service` - Added GPIO permissions  
✅ `README.md` - Complete DHT22 documentation  

## Files Added

✨ `docs/DHT22_SETUP.md` - Comprehensive hardware guide  
✨ `DEPLOYMENT_CHECKLIST_DHT22.md` - Deployment verification  
✨ `DHT22_INTEGRATION_SUMMARY.md` - Integration overview  

## GPIO Pinout Reference

```
[USB] ┐
      │  1  2  ← Pin 1: 3.3V (VCC)
      │  3  4
      │  5  6  ← Pin 6: GND
      │  7  8  ← Pin 7: GPIO4 (DATA)
      │  9 10
      ...
```

## Next Steps

1. ✅ Wire DHT22 to GPIO4 and GND/3.3V
2. ✅ Run installation scripts
3. ✅ Test sensor: `python3 -m sensors.dht22`
4. ✅ Reboot and verify GUI shows readings
5. ✅ Check logs if issues: `journalctl -u rpi_gui.service -f`

## Documentation

📖 **DHT22_SETUP.md** - Complete hardware & software guide  
📖 **DEPLOYMENT_CHECKLIST_DHT22.md** - Step-by-step verification  
📖 **README.md** - Project overview with sensor section  
📖 **DHT22_INTEGRATION_SUMMARY.md** - What's been updated  

## Support

For detailed help, see:
- **Hardware issues**: See [docs/DHT22_SETUP.md](docs/DHT22_SETUP.md)
- **Deployment help**: See [DEPLOYMENT_CHECKLIST_DHT22.md](DEPLOYMENT_CHECKLIST_DHT22.md)
- **Code changes**: See [DHT22_INTEGRATION_SUMMARY.md](DHT22_INTEGRATION_SUMMARY.md)

---

**Status**: ✅ Ready for deployment  
**Updated**: December 28, 2025
