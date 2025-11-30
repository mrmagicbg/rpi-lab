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
    # Touch event state
    touch_action = {"action": None}

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
        x, y = 0, 0
        while True:
            for event in dev.read_loop():
                logger.debug(f"Touch event: {event}")
                if event.type == ecodes.EV_ABS:
                    if event.code == ecodes.ABS_X:
                        x = event.value
                    elif event.code == ecodes.ABS_Y:
                        y = event.value
                elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH and event.value == 1:
                    logger.info(f"Touch at x={x}, y={y}")
                    # Map touch coordinates to button
                    # Assume display is 800x480, adjust as needed
                    if 400 < y < 480:
                        btn_width = 200
                        idx = x // btn_width
                        logger.info(f"Touch mapped to button idx={idx}")
                        if 0 <= idx < len(BUTTONS):
                            touch_action["action"] = BUTTONS[idx]["action"]
            time.sleep(0.01)

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
        # Handle touch actions
        if touch_action["action"]:
            logger.info(f"Touch action: {touch_action['action']}")
            if touch_action["action"] == "up" and current_row > 0:
                current_row -= 1
            elif touch_action["action"] == "down" and current_row < len(MENU) - 1:
                current_row += 1
            elif touch_action["action"] == "enter":
                if current_row == 0:
                    run_rf_script()
                elif current_row == 1:
                    reboot_pi()
                elif current_row == 2:
                    open_shell()
                elif current_row == 3:
                    break
            elif touch_action["action"] == "cancel":
                break
            touch_action["action"] = None


def setup_curses():
    curses.wrapper(_curses_main)


def _curses_main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    main_menu(stdscr)


if __name__ == "__main__":
    setup_curses()
