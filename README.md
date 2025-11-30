# RPI Lab

This repository holds Raspberry Pi-related tools and utilities grouped by area:

- `rf/` — existing RF-related tools and Pi setup scripts
- `display/` — scripts to configure displays (Waveshare DSI panels etc.)
- `tui/` — TUI (console) application and systemd service to run on boot

Deployment / setup for a Raspberry Pi 3 (summary)

1) Prepare the Pi

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip
```

2) Copy repository to the Pi (recommended location `/opt`)

```bash
# on the Pi or via scp from your workstation
sudo cp -r ~/rpi-lab /opt/rpi-lab
sudo chown -R root:root /opt/rpi-lab || true
```

3) Install and configure components using the `install/` helpers

- Display (Waveshare 4.3" DSI):

```bash
sudo bash /opt/rpi-lab/install/display_install.sh
# This runs the display installer in non-interactive mode (no reboot).
```

- RF setup (if applicable):

```bash
sudo bash /opt/rpi-lab/install/install_rf.sh
```

- TUI service + venv (creates a venv at `/opt/rpi-lab/.venv` and enables the systemd service):

```bash
sudo bash /opt/rpi-lab/install/install_service.sh
```

Notes:
- The `install/` folder contains helpers: `display_install.sh`, `install_rf.sh`, `install_service.sh`, `venv_setup.sh`.
- The TUI runs on `tty1` by default; edit `tui/rpi_tui.service` if you prefer a different TTY or user.
- Touch support requires input drivers; `display_install.sh` installs `xserver-xorg-input-evdev` and calibration tools. The script attempts to install `tslib` for touch support, but if it is not available in your distribution, it will try to install `libts-bin` as a fallback. If neither package is available, you may need to manually install touch support or consult your OS documentation for alternatives.

4) Run the TUI manually (inside venv)

```bash
source /opt/rpi-lab/.venv/bin/activate
python /opt/rpi-lab/tui/rpi_tui.py
```

If you want additional features (logging, user selection, network checks), open an issue or request in the repo.

Touch testing & calibration
---------------------------

- The TUI now includes a debug area showing raw and scaled touch coordinates and press state.
- Install `evtest` to verify the device produces events:

```bash
sudo apt-get update
sudo apt-get install -y evtest
sudo evtest /dev/input/event0
```

- Run the TUI directly to see the debug area on the console:

```bash
sudo /opt/rpi-lab/.venv/bin/python /opt/rpi-lab/tui/rpi_tui.py
```

- If touch coordinates look large (e.g. 0..32767), the TUI will auto-scale them. If mapping is off, note the raw X/Y values shown in the debug area and I can help tune the scaling constants.
