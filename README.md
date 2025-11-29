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

2) Display setup (Waveshare 4.3" DSI)

```bash
cd ~/Code/GitHub/mrmagicbg/rpi-lab/display
sudo ./setup_waveshare_4.3inch_dsi.sh
```

Follow any on-screen instructions and reboot the Pi when prompted.

3) TUI install and auto-start

```bash
# copy repository to /opt or keep in home and point service ExecStart accordingly
sudo cp -r ~/Code/GitHub/mrmagicbg/rpi-lab /opt/rpi-lab
sudo chown -R root:root /opt/rpi-lab || true

# install the systemd service (adjust path if necessary)
sudo cp /opt/rpi-lab/tui/rpi_tui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rpi_tui.service
sudo systemctl start rpi_tui.service
```

Notes:
- The TUI uses `curses` and works on a console TTY; the provided systemd service runs in `multi-user.target`. If you want it on a specific TTY adjust the service (see `StandardInput=tty` / `TTYPath=` options).
- Touch support requires input drivers (installed by the display script). If running under X11 you may need to configure calibration.

4) Running manually

```bash
python3 /opt/rpi-lab/tui/rpi_tui.py
```

If you want additional features (logging, user selection, network checks), open an issue or request in the repo.
