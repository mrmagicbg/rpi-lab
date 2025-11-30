#!/usr/bin/env python3
"""
Advanced RPI TUI launcher for RF tools and system actions.

Features:
- Runs RF setup script (from `rf/`)
- Reboots the Pi
- Drops to an interactive shell
- Large text and on-screen buttons (Up, Down, Enter, Cancel)
- Touch support via evdev (raspberrypi-ts)
- Designed for console (TTY) on Waveshare DSI display

Requirements:
- python3-evdev (installed by display_install.sh)
- Touch device at /dev/input/event0
"""

from __future__ import annotations
import os
import subprocess
import curses
import logging
import threading
import time
try:
    from evdev import InputDevice, categorize, ecodes, AbsEvent
except ImportError:
    InputDevice = None
    AbsEvent = None
    ecodes = None
    categorize = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('rpi_tui')

BUTTONS = [
    {"label": "↑", "action": "up"},
    {"label": "↓", "action": "down"},
    {"label": "Enter", "action": "enter"},
    {"label": "Cancel", "action": "cancel"}
]
MENU = [
    "Run RF Script(s)",
    "Reboot Raspberry Pi",
    "Open Shell (CLI)",
    "Exit"
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RF_SCRIPT_PATH = os.path.join(BASE_DIR, 'rf', 'setup_pi.sh')


def run_rf_script():
    if not os.path.isfile(RF_SCRIPT_PATH):
        logger.error("RF script not found: %s", RF_SCRIPT_PATH)
        return
    logger.info("Running RF script: %s", RF_SCRIPT_PATH)
    subprocess.call(['bash', RF_SCRIPT_PATH])


def reboot_pi():
    logger.info("Reboot requested")
    subprocess.call(['sudo', 'reboot'])


def open_shell():
    logger.info("Opening shell. Type 'exit' to return to TUI.")
    # Spawn an interactive shell attached to current tty
    subprocess.call(os.environ.get('SHELL', '/bin/bash'))


def main_menu(stdscr):
    # Thread-safe touch state
    touch_state = {
        "raw_x": None,
        "raw_y": None,
        "pressed": False,
        "x_min": None,
        "x_max": None,
        "y_min": None,
        "y_max": None,
    }
    touch_lock = threading.Lock()

    def touch_thread():
        if not InputDevice:
            logger.warning("evdev not available, touch will not work.")
            return
        try:
            dev = InputDevice('/dev/input/event0')
            logger.info("Touch device opened: /dev/input/event0")
        except Exception as e:
            logger.warning(f"Touch device not found: {e}")
            return

        # Try to read absolute axis ranges
        try:
            xinfo = dev.absinfo(ecodes.ABS_X)
            yinfo = dev.absinfo(ecodes.ABS_Y)
            with touch_lock:
                touch_state['x_min'] = xinfo.min
                touch_state['x_max'] = xinfo.max
                touch_state['y_min'] = yinfo.min
                touch_state['y_max'] = yinfo.max
            logger.info(f"Touch ranges X: {xinfo.min}..{xinfo.max} Y: {yinfo.min}..{yinfo.max}")
        except Exception:
            logger.debug('Could not read ABS ranges; using defaults')

        raw_x, raw_y = 0, 0
        for event in dev.read_loop():
            logger.debug(f"Touch event: {event}")
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_X:
                    raw_x = event.value
                    with touch_lock:
                        touch_state['raw_x'] = raw_x
                elif event.code == ecodes.ABS_Y:
                    raw_y = event.value
                    with touch_lock:
                        touch_state['raw_y'] = raw_y
            elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                # value 1 = press, 0 = release
                pressed = bool(event.value)
                with touch_lock:
                    touch_state['pressed'] = pressed
                logger.info(f"Touch {'pressed' if pressed else 'released'} raw_x={raw_x} raw_y={raw_y}")
            # loop continues reading events

    threading.Thread(target=touch_thread, daemon=True).start()

    curses.curs_set(0)
    current_row = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "RPI TUI"
        # Draw title (extra large)
        try:
            stdscr.addstr(1, w // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)
        except curses.error:
            pass
        # Draw menu with large text, close together
        for idx, row in enumerate(MENU):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(MENU) // 2 + idx * 2
            try:
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, row.upper(), curses.A_BOLD)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, row.upper(), curses.A_BOLD)
            except curses.error:
                pass
        # Draw boxed debug area for touch info
        dbg_h, dbg_w = 5, 38
        try:
            dbg_x = 2
            dbg_y = 2
            # box border
            stdscr.attron(curses.A_DIM)
            for bx in range(dbg_w):
                stdscr.addch(dbg_y, dbg_x + bx, ' ')
                stdscr.addch(dbg_y + dbg_h - 1, dbg_x + bx, ' ')
            for by in range(dbg_h):
                stdscr.addch(dbg_y + by, dbg_x, ' ')
                stdscr.addch(dbg_y + by, dbg_x + dbg_w - 1, ' ')
            stdscr.attroff(curses.A_DIM)
        except curses.error:
            pass

        # Read touch_state safely
        with touch_lock:
            raw_x = touch_state.get('raw_x')
            raw_y = touch_state.get('raw_y')
            pressed = touch_state.get('pressed')
            x_min = touch_state.get('x_min')
            x_max = touch_state.get('x_max')
            y_min = touch_state.get('y_min')
            y_max = touch_state.get('y_max')

        # Scale raw to terminal coords if possible
        scaled_x = None
        scaled_y = None
        if raw_x is not None and x_min is not None and x_max and raw_y is not None and y_min is not None and y_max:
            try:
                scaled_x = int((raw_x - x_min) * (w - 1) / (x_max - x_min))
                scaled_y = int((raw_y - y_min) * (h - 1) / (y_max - y_min))
            except Exception:
                scaled_x = None
                scaled_y = None
        else:
            # fallback heuristics: assume raw range 0..32767
            if raw_x is not None:
                try:
                    scaled_x = int(raw_x * (w - 1) / 32767)
                except Exception:
                    scaled_x = None
            if raw_y is not None:
                try:
                    scaled_y = int(raw_y * (h - 1) / 32767)
                except Exception:
                    scaled_y = None

        dbg_lines = [
            f"rawX:{raw_x} rawY:{raw_y}",
            f"sclX:{scaled_x} sclY:{scaled_y}",
            f"pressed:{pressed}"
        ]
        try:
            for i, line in enumerate(dbg_lines):
                stdscr.addstr(dbg_y + 1 + i, dbg_x + 1, line.ljust(dbg_w - 2), curses.A_DIM)
        except curses.error:
            pass
        # Draw much bigger buttons at bottom
        btn_y = h - 4
        btn_width = w // len(BUTTONS)
        for idx, btn in enumerate(BUTTONS):
            bx = idx * btn_width
            try:
                stdscr.attron(curses.color_pair(2))
                # Make button label very wide and centered
                stdscr.addstr(btn_y, bx + 1, btn["label"].center(btn_width - 2), curses.A_BOLD | curses.A_REVERSE)
                stdscr.attroff(curses.color_pair(2))
            except curses.error:
                pass
        stdscr.refresh()
        # Handle keyboard
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(MENU) - 1:
            current_row += 1
        elif key in [curses.KEY_ENTER, ord('\n')]:
            if current_row == 0:
                run_rf_script()
            elif current_row == 1:
                reboot_pi()
            elif current_row == 2:
                open_shell()
            elif current_row == 3:
                break
        # Handle touch press -> map to buttons using scaled coords
        if pressed and scaled_x is not None and scaled_y is not None:
            # consider button row at bottom 3 rows of terminal
            if scaled_y >= (h - 3):
                idx = int(scaled_x * len(BUTTONS) / max(1, w))
                if 0 <= idx < len(BUTTONS):
                    action = BUTTONS[idx]['action']
                    logger.info(f"Touch button idx={idx} action={action}")
                    if action == 'up' and current_row > 0:
                        current_row -= 1
                    elif action == 'down' and current_row < len(MENU) - 1:
                        current_row += 1
                    elif action == 'enter':
                        if current_row == 0:
                            run_rf_script()
                        elif current_row == 1:
                            reboot_pi()
                        elif current_row == 2:
                            open_shell()
                        elif current_row == 3:
                            break
                    elif action == 'cancel':
                        break


def setup_curses():
    curses.wrapper(_curses_main)


def _curses_main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    main_menu(stdscr)


if __name__ == "__main__":
    setup_curses()
