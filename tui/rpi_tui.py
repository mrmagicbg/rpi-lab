#!/usr/bin/env python3
"""Simple RPI TUI launcher for rf tools and system actions.

Features:
- Runs RF setup script (from `rf/`)
- Reboots the Pi
- Drops to an interactive shell
- Designed to run on the console (TTY) and supports touch/mouse events via curses
"""

from __future__ import annotations
import os
import subprocess
import curses
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('rpi_tui')

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
    curses.curs_set(0)
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    except Exception:
        logger.debug('Mouse support not available')
    current_row = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "RPI TUI"
        try:
            stdscr.addstr(1, w // 2 - len(title) // 2, title, curses.A_BOLD)
        except curses.error:
            pass
        for idx, row in enumerate(MENU):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(MENU) // 2 + idx
            try:
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, row)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, row)
            except curses.error:
                pass
        stdscr.refresh()
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
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                # Map mouse click to menu item
                for idx in range(len(MENU)):
                    y = h // 2 - len(MENU) // 2 + idx
                    if my == y:
                        current_row = idx
                        if bstate & curses.BUTTON1_CLICKED:
                            if current_row == 0:
                                run_rf_script()
                            elif current_row == 1:
                                reboot_pi()
                            elif current_row == 2:
                                open_shell()
                            elif current_row == 3:
                                return
            except Exception:
                logger.exception("Mouse event handling failed")


def setup_curses():
    curses.wrapper(_curses_main)


def _curses_main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    main_menu(stdscr)


if __name__ == "__main__":
    setup_curses()
