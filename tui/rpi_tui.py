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
    logger.info("Main menu initializing...")
    logger.info(f"Terminal size: {stdscr.getmaxyx()}")
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
        
        # Find the touchscreen device
        touchscreen_device = None
        try:
            from evdev import list_devices
            devices = [InputDevice(path) for path in list_devices()]
            for dev in devices:
                logger.info(f"Found input device: {dev.path} - {dev.name}")
                # Look for touchscreen devices
                if 'touchscreen' in dev.name.lower() or 'goodix' in dev.name.lower() or 'capacitive' in dev.name.lower():
                    touchscreen_device = dev.path
                    logger.info(f"Using touchscreen device: {dev.path} - {dev.name}")
                    break
            
            # Fallback to common event devices if no touchscreen found
            if not touchscreen_device:
                for event_num in range(10):  # Check event0 through event9
                    event_path = f'/dev/input/event{event_num}'
                    try:
                        dev = InputDevice(event_path)
                        logger.info(f"Checking {event_path}: {dev.name}")
                        # Check if it has touch capabilities
                        caps = dev.capabilities()
                        if ecodes.EV_ABS in caps and (ecodes.ABS_X in caps[ecodes.EV_ABS] or getattr(ecodes, 'ABS_MT_POSITION_X', None) in caps[ecodes.EV_ABS]):
                            touchscreen_device = event_path
                            logger.info(f"Using detected touch device: {event_path} - {dev.name}")
                            break
                    except Exception as e:
                        logger.debug(f"Could not check {event_path}: {e}")
                        continue
        except Exception as e:
            logger.warning(f"Error detecting touchscreen device: {e}")
        
        if not touchscreen_device:
            logger.warning("No touchscreen device found, touch will not work.")
            return
        
        try:
            dev = InputDevice(touchscreen_device)
            logger.info(f"Touch device opened: {touchscreen_device}")
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
            logger.info(f"Touch ranges detected - X: {xinfo.min}..{xinfo.max} Y: {yinfo.min}..{yinfo.max}")
        except Exception as e:
            logger.warning(f'Could not read ABS ranges: {e}; using defaults')

        raw_x, raw_y = None, None
        last_syn_time = 0
        last_press_time = 0
        SYN_DEBOUNCE = 0.25
        for event in dev.read_loop():
            logger.debug(f"Touch event: {event}")
            if event.type == ecodes.EV_ABS:
                # Support both absolute and multitouch axes
                if event.code in (ecodes.ABS_X, getattr(ecodes, 'ABS_MT_POSITION_X', None)):
                    raw_x = event.value
                    with touch_lock:
                        touch_state['raw_x'] = raw_x
                    logger.debug(f"Touch X: {raw_x}")
                elif event.code in (ecodes.ABS_Y, getattr(ecodes, 'ABS_MT_POSITION_Y', None)):
                    raw_y = event.value
                    with touch_lock:
                        touch_state['raw_y'] = raw_y
                    logger.debug(f"Touch Y: {raw_y}")
            elif event.type == ecodes.EV_KEY and event.code == getattr(ecodes, 'BTN_TOUCH', None):
                # value 1 = press, 0 = release
                pressed = bool(event.value)
                with touch_lock:
                    touch_state['pressed'] = pressed
                    if pressed:
                        touch_state['last_press_time'] = time.time()
                logger.info(f"Touch {'pressed' if pressed else 'released'} raw_x={raw_x} raw_y={raw_y}")
            elif event.type == ecodes.EV_SYN and event.code == getattr(ecodes, 'SYN_REPORT', 0):
                # Some drivers only send ABS updates followed by SYN_REPORT; treat that as a tap
                now = time.time()
                if raw_x is not None and raw_y is not None and (now - last_press_time) > SYN_DEBOUNCE:
                    # register a short press
                    with touch_lock:
                        touch_state['pressed'] = True
                        touch_state['last_press_time'] = now
                    logger.info(f"SYN_REPORT detected; treating as press raw_x={raw_x} raw_y={raw_y}")
                    last_press_time = now
                    # leave pressed True briefly; a later loop iteration will handle mapping
                    # schedule release after small delay
                    def release_after(delay=0.15):
                        time.sleep(delay)
                        with touch_lock:
                            touch_state['pressed'] = False
                    threading.Thread(target=release_after, daemon=True).start()
            # continue loop

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
        
        logger.debug(f"Main loop touch state: raw_x={raw_x}, raw_y={raw_y}, pressed={pressed}")

        # Scale raw to terminal coords if possible
        scaled_x = None
        scaled_y = None
        if raw_x is not None and x_min is not None and x_max and raw_y is not None and y_min is not None and y_max:
            try:
                scaled_x = int((raw_x - x_min) * (w - 1) / (x_max - x_min))
                scaled_y = int((raw_y - y_min) * (h - 1) / (y_max - y_min))
                logger.debug(f"Scaled using ranges: raw_x={raw_x}({x_min}-{x_max}) -> scaled_x={scaled_x}, raw_y={raw_y}({y_min}-{y_max}) -> scaled_y={scaled_y}")
            except Exception as e:
                logger.warning(f"Error scaling coordinates: {e}")
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
            logger.debug(f"Scaled using fallback: raw_x={raw_x} -> scaled_x={scaled_x}, raw_y={raw_y} -> scaled_y={scaled_y}")

        # Debug touch state
        logger.debug(f"Touch state: raw_x={raw_x}, raw_y={raw_y}, pressed={pressed}, scaled_x={scaled_x}, scaled_y={scaled_y}")

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
        touch_processed = False
        if pressed and scaled_x is not None and scaled_y is not None:
            logger.info(f"Touch detected: scaled_x={scaled_x}, scaled_y={scaled_y}, terminal_h={h}, button_row={h-4}")
            # consider button row at bottom 4 rows of terminal (matches btn_y = h - 4)
            if scaled_y >= (h - 4):
                idx = int(scaled_x * len(BUTTONS) / max(1, w))
                if 0 <= idx < len(BUTTONS):
                    action = BUTTONS[idx]['action']
                    logger.info(f"Touch button idx={idx} action={action}")
                    touch_processed = True
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
        
        # Also check for recent touch events (within last 0.2 seconds)
        with touch_lock:
            last_press = touch_state.get('last_press_time', 0)
        if not touch_processed and time.time() - last_press < 0.2 and scaled_x is not None and scaled_y is not None:
            logger.info(f"Processing recent touch: scaled_x={scaled_x}, scaled_y={scaled_y}")
            if scaled_y >= (h - 4):
                idx = int(scaled_x * len(BUTTONS) / max(1, w))
                if 0 <= idx < len(BUTTONS):
                    action = BUTTONS[idx]['action']
                    logger.info(f"Recent touch button idx={idx} action={action}")
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
    logger.info("Setting up curses...")
    curses.wrapper(_curses_main)


def _curses_main(stdscr):
    logger.info("Curses initialized, starting main menu...")
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    main_menu(stdscr)


if __name__ == "__main__":
    logger.info("RPI TUI starting up...")
    try:
        setup_curses()
        logger.info("RPI TUI exited normally")
    except Exception as e:
        logger.error(f"RPI TUI crashed with error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
