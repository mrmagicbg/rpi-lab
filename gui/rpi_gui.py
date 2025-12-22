#!/usr/bin/env python3
"""
RPI GUI launcher for RF tools, sensor monitoring, and system actions.

Features:
- Large touch-friendly buttons (800x480 Waveshare 4.3" DSI display)
- DHT22 temperature and humidity sensor readings
- Runs RF setup script (from `rf/`)
- Reboots the Pi
- Drops to an interactive shell in a terminal
- Clean exit
- Auto-detects ft5x06 touch device via evdev

Requirements:
- tkinter (python3-tk)
- evdev (installed via requirements.txt into venv)
- Adafruit_DHT (for DHT22 sensor)
- X11 or Wayland display server
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import logging

# Import DHT22 sensor module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sensors.dht22 import DHT22Sensor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rpi_gui')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RF_SCRIPT_PATH = os.path.join(BASE_DIR, 'rf', 'setup_pi.sh')

# Initialize DHT22 sensor (GPIO4 by default)
DHT_SENSOR = DHT22Sensor(gpio_pin=4)


class RPILauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RPI Lab - Control Panel")
        
        # Get screen dimensions (800x480 for Waveshare 4.3")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        logger.info(f"Screen resolution: {screen_width}x{screen_height}")
        
        # Fullscreen on touch display
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.attributes('-fullscreen', True)
        
        # Dark theme with large, touch-friendly elements
        self.root.configure(bg='#1e1e1e')
        
        # Title label
        title = tk.Label(
            self.root,
            text="RPI Lab Control Panel",
            font=('Arial', 28, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e',
            pady=20
        )
        title.pack()
        
        # Button container frame
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(expand=True, fill='both', padx=30, pady=10)
        
        # Large touch buttons (each ~100px tall minimum)
        button_config = {
            'font': ('Arial', 20, 'bold'),
            'width': 25,
            'height': 2,
            'relief': 'raised',
            'bd': 5,
            'bg': '#2d89ef',
            'fg': 'white',
            'activebackground': '#1e5fa8',
            'activeforeground': 'white'
        }
        
        # Menu buttons matching TUI functionality
        btn_rf = tk.Button(
            button_frame,
            text="🔧 Run RF Script(s)",
            command=self.run_rf_script,
            **button_config
        )
        btn_rf.pack(pady=10, fill='x')
        
        btn_sensors = tk.Button(
            button_frame,
            text="🌡️ Sensor Readings",
            command=self.show_sensors,
            bg='#ff8c00',
            activebackground='#cc6600',
            **{k: v for k, v in button_config.items() if k not in ['bg', 'activebackground']}
        )
        btn_sensors.pack(pady=10, fill='x')
        
        btn_reboot = tk.Button(
            button_frame,
            text="🔄 Reboot Raspberry Pi",
            command=self.reboot_pi,
            bg='#e81123',
            activebackground='#a50011',
            **{k: v for k, v in button_config.items() if k not in ['bg', 'activebackground']}
        )
        btn_reboot.pack(pady=10, fill='x')
        
        btn_shell = tk.Button(
            button_frame,
            text="💻 Open Shell (Terminal)",
            command=self.open_shell,
            bg='#00a300',
            activebackground='#007000',
            **{k: v for k, v in button_config.items() if k not in ['bg', 'activebackground']}
        )
        btn_shell.pack(pady=10, fill='x')
        
        btn_exit = tk.Button(
            button_frame,
            text="❌ Exit",
            command=self.exit_app,
            bg='#555555',
            activebackground='#333333',
            **{k: v for k, v in button_config.items() if k not in ['bg', 'activebackground']}
        )
        btn_exit.pack(pady=10, fill='x')
        
        # Footer with instructions
        footer = tk.Label(
            self.root,
            text="Touch buttons to perform actions • Press F11 to toggle fullscreen",
            font=('Arial', 10),
            fg='#888888',
            bg='#1e1e1e',
            pady=10
        )
        footer.pack(side='bottom')
        
        # Keyboard shortcuts
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', lambda e: self.exit_app())
        
        logger.info("GUI initialized successfully")
    
    def run_rf_script(self):
        """Execute the RF setup script in a terminal"""
        logger.info("RF Script button pressed")
        if not os.path.isfile(RF_SCRIPT_PATH):
            logger.error(f"RF script not found: {RF_SCRIPT_PATH}")
            messagebox.showerror(
                "Script Not Found",
                f"RF script not found at:\n{RF_SCRIPT_PATH}"
            )
            return
        
        logger.info(f"Running RF script: {RF_SCRIPT_PATH}")
        try:
            # Run in xterm or fallback terminal
            terminals = ['x-terminal-emulator', 'xterm', 'lxterminal', 'gnome-terminal']
            for term in terminals:
                if subprocess.call(['which', term], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    subprocess.Popen([term, '-e', f'bash {RF_SCRIPT_PATH}; read -p "Press Enter to close..."'])
                    break
            else:
                # Fallback: run directly and show message
                subprocess.call(['bash', RF_SCRIPT_PATH])
                messagebox.showinfo("RF Script", "RF script execution completed.")
        except Exception as e:
            logger.error(f"Failed to run RF script: {e}")
            messagebox.showerror("Error", f"Failed to run RF script:\n{e}")
    
    def show_sensors(self):
        """Display DHT22 sensor readings in a popup window"""
        logger.info("Sensor Readings button pressed")
        
        # Create popup window
        sensor_window = tk.Toplevel(self.root)
        sensor_window.title("Sensor Readings")
        sensor_window.geometry("700x500")
        sensor_window.configure(bg='#1e1e1e')
        sensor_window.transient(self.root)
        sensor_window.grab_set()
        
        # Title
        title = tk.Label(
            sensor_window,
            text="DHT22 Sensor Readings",
            font=('Arial', 24, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e',
            pady=20
        )
        title.pack()
        
        # Sensor data frame
        data_frame = tk.Frame(sensor_window, bg='#2d2d2d', relief='raised', bd=3)
        data_frame.pack(padx=30, pady=20, fill='both', expand=True)
        
        # Temperature label
        temp_label = tk.Label(
            data_frame,
            text="Temperature:",
            font=('Arial', 18, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d',
            pady=10
        )
        temp_label.pack()
        
        temp_value = tk.Label(
            data_frame,
            text="Reading...",
            font=('Arial', 36, 'bold'),
            fg='#ff6b6b',
            bg='#2d2d2d',
            pady=5
        )
        temp_value.pack()
        
        # Humidity label
        humid_label = tk.Label(
            data_frame,
            text="Humidity:",
            font=('Arial', 18, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d',
            pady=10
        )
        humid_label.pack()
        
        humid_value = tk.Label(
            data_frame,
            text="Reading...",
            font=('Arial', 36, 'bold'),
            fg='#4ecdc4',
            bg='#2d2d2d',
            pady=5
        )
        humid_value.pack()
        
        # Status label
        status_label = tk.Label(
            data_frame,
            text="",
            font=('Arial', 12),
            fg='#888888',
            bg='#2d2d2d',
            pady=10
        )
        status_label.pack()
        
        # Read sensor
        def update_readings():
            temp_str, humid_str = DHT_SENSOR.read_formatted()
            temp_value.config(text=temp_str)
            humid_value.config(text=humid_str)
            
            if temp_str == "N/A":
                status_label.config(
                    text="⚠️ Sensor not connected or reading failed\n(GPIO4, physical pin 7)",
                    fg='#ffaa00'
                )
            else:
                status_label.config(
                    text="✓ Sensor reading successful (GPIO4)",
                    fg='#00ff88'
                )
        
        # Refresh button
        refresh_btn = tk.Button(
            sensor_window,
            text="🔄 Refresh",
            command=update_readings,
            font=('Arial', 16, 'bold'),
            bg='#2d89ef',
            fg='white',
            activebackground='#1e5fa8',
            width=15,
            height=1,
            relief='raised',
            bd=3
        )
        refresh_btn.pack(pady=10)
        
        # Close button
        close_btn = tk.Button(
            sensor_window,
            text="✕ Close",
            command=sensor_window.destroy,
            font=('Arial', 16, 'bold'),
            bg='#555555',
            fg='white',
            activebackground='#333333',
            width=15,
            height=1,
            relief='raised',
            bd=3
        )
        close_btn.pack(pady=5)
        
        # Initial reading
        update_readings()
    
    def reboot_pi(self):
        """Reboot the Raspberry Pi after confirmation"""
        logger.info("Reboot button pressed")
        if messagebox.askyesno("Confirm Reboot", "Reboot Raspberry Pi now?"):
            logger.info("Reboot confirmed")
            try:
                subprocess.Popen(['sudo', 'reboot'])
            except Exception as e:
                logger.error(f"Failed to reboot: {e}")
                messagebox.showerror("Error", f"Failed to reboot:\n{e}")
    
    def open_shell(self):
        """Open a terminal window"""
        logger.info("Shell button pressed")
        try:
            # Try different terminal emulators
            terminals = ['x-terminal-emulator', 'xterm', 'lxterminal', 'gnome-terminal']
            for term in terminals:
                if subprocess.call(['which', term], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    subprocess.Popen([term])
                    break
            else:
                messagebox.showwarning("No Terminal", "No terminal emulator found.\nInstall xterm: sudo apt install xterm")
        except Exception as e:
            logger.error(f"Failed to open shell: {e}")
            messagebox.showerror("Error", f"Failed to open shell:\n{e}")
    
    def exit_app(self):
        """Exit the application"""
        logger.info("Exit button pressed")
        if messagebox.askyesno("Confirm Exit", "Exit RPI Lab GUI?"):
            logger.info("Exit confirmed")
            self.root.quit()
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
        logger.info(f"Fullscreen: {not current}")


def main():
    """Main entry point"""
    logger.info("Starting RPI Lab GUI...")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Base directory: {BASE_DIR}")
    
    root = tk.Tk()
    app = RPILauncherGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"GUI error: {e}", exc_info=True)
        raise
    finally:
        logger.info("GUI shutting down")


if __name__ == '__main__':
    main()
