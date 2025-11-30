RPI TUI service
================

The TUI (Text User Interface) provides a console-based menu system for Raspberry Pi operations including RF script execution, system reboot, and shell access. Features touchscreen support with on-screen navigation buttons.

If you change the unit file `rpi_tui.service`, reload systemd and (re)enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rpi_tui.service
```

The service includes a short startup delay to allow the system to reach `multi-user.target`.

**Recent Improvements:**
- Enhanced touchscreen support with improved coordinate mapping
- Detailed touch event logging for debugging
- More reliable touch button detection
- Better handling of different touchscreen drivers

Quick setup
-----------

1) Create a virtualenv and install dependencies (the `install/venv_setup.sh` helper does this):

```bash
sudo /opt/rpi-lab/install/venv_setup.sh
```

2) The service is defined in `tui/rpi_tui.service`. After editing run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rpi_tui.service
sudo systemctl status rpi_tui.service -l
```

Manual run (debug)
------------------

To run the TUI interactively and see logs / tracebacks:

```bash
source /opt/rpi-lab/.venv/bin/activate
sudo /opt/rpi-lab/.venv/bin/python /opt/rpi-lab/tui/rpi_tui.py
```

Service notes and troubleshooting
--------------------------------

- The unit uses a short startup delay implemented inside the ExecStart command to avoid systemd signalling issues with `ExecStartPre`.
- If the service fails to start, check the journal for tracebacks:

```bash
sudo journalctl -xeu rpi_tui.service --no-pager
```

- Common causes:
	- Virtualenv path missing: confirm `/opt/rpi-lab/.venv/bin/python` exists.
	- Permission error on `/dev/tty1`: verify the service runs as a user with access to the TTY or run as `root`.
	- Python import/runtime error: run the script manually (see Manual run) and capture the traceback.
	- Touch not working: check that evdev is installed and `/dev/input/event0` exists. The TUI logs detailed touch coordinates for debugging.

start.sh wrapper
----------------

This repo contains `tui/start.sh` which is a small wrapper that sleeps, cds into the TUI directory, and execs the Python script. The systemd unit calls the inline shell command that also performs a sleep; if you prefer to use `start.sh` directly, make it executable:

```bash
sudo chmod +x /opt/rpi-lab/tui/start.sh
```

If you'd like, I can make `start.sh` executable in the repo and update the install helper to set the permission automatically. Let me know if you want that change.

