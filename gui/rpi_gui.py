#!/usr/bin/env python3
"""
RPI GUI launcher for RF tools, sensor monitoring, and system actions.

Features:
- Large uniform touch-friendly buttons (800x480 Waveshare 4.3" DSI display)
- Live DHT22 temperature and humidity sensor display
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
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Title label
        title = tk.Label(
            main_frame,
            text="RPI Lab Control Panel",
            font=('Arial', 24, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e',
            pady=10
        )
        title.pack()
        
        # Sensor display area
        self.sensor_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=3)
        self.sensor_frame.pack(fill='x', padx=10, pady=10)
        
        sensor_title = tk.Label(
            self.sensor_frame,
            text="DHT22 Sensor (GPIO4)",
            font=('Arial', 14, 'bold'),
            fg='#00ff88',
            bg='#2d2d2d',
            pady=5
        )
        sensor_title.pack()
        
        # Sensor readings container
        sensor_data_frame = tk.Frame(self.sensor_frame, bg='#2d2d2d')
        sensor_data_frame.pack(pady=5)
        
        # Temperature display
        temp_container = tk.Frame(sensor_data_frame, bg='#2d2d2d')
        temp_container.pack(side='left', padx=20)
        
        tk.Label(
            temp_container,
            text="🌡️ Temp:",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack()
        
        self.temp_label = tk.Label(
            temp_container,
            text="--°C",
            font=('Arial', 20, 'bold'),
            fg='#ff6b6b',
            bg='#2d2d2d'
        )
        self.temp_label.pack()
        
        # Humidity display
        humid_container = tk.Frame(sensor_data_frame, bg='#2d2d2d')
        humid_container.pack(side='left', padx=20)
        
        tk.Label(
            humid_container,
            text="💧 Humidity:",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack()
        
        self.humid_label = tk.Label(
            humid_container,
            text="--%",
            font=('Arial', 20, 'bold'),
            fg='#4ecdc4',
            bg='#2d2d2d'
        )
        self.humid_label.pack()
        
        # Status label
        self.sensor_status = tk.Label(
            self.sensor_frame,
            text="Initializing sensor...",
            font=('Arial', 9),
            fg='#888888',
            bg='#2d2d2d',
            pady=5
        )
        self.sensor_status.pack()
        
        # Button container frame
        button_frame = tk.Frame(main_frame, bg='#1e1e1e')
        button_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # UNIFORM touch buttons - all same size
        button_config = {
            'font': ('Arial', 18, 'bold'),
            'width': 20,
            'height': 2,
            'relief': 'raised',
            'bd': 4,
            'fg': 'white'
        }
        
        # Menu buttons - all uniform size
        btn_rf = tk.Button(
            button_frame,
            text="🔧 Run RF Script(s)",
            command=self.run_rf_script,
            bg='#2d89ef',
            activebackground='#1e5fa8',
            **button_config
        )
        btn_rf.pack(pady=5, fill='x')
        
        btn_reboot = tk.Button(
            button_frame,
            text="🔄 Reboot System",
            command=self.reboot_pi,
            bg='#e81123',
            activebackground='#a50011',
            **button_config
        )
        btn_reboot.pack(pady=5, fill='x')
        
        btn_shell = tk.Button(
            button_frame,
            text="💻 Open Terminal",
            command=self.open_shell,
            bg='#00a300',
            activebackground='#007000',
            **button_config
        )
        btn_shell.pack(pady=5, fill='x')
        
        btn_exit = tk.Button(
            button_frame,
            text="❌ Exit Application",
            command=self.exit_app,
            bg='#555555',
            activebackground='#333333',
            **button_config
        )
        btn_exit.pack(pady=5, fill='x')
        
        # Footer with instructions
        footer = tk.Label(
            self.root,
            text="Touch buttons to perform actions • F11: fullscreen • ESC: exit",
            font=('Arial', 9),
            fg='#666666',
            bg='#1e1e1e',
            pady=5
        )
        footer.pack(side='bottom')
        
        # Keyboard shortcuts
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', lambda e: self.exit_app())
        
        # Start sensor update loop
        self.update_sensor_readings()
        
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
    
    def update_sensor_readings(self):
        """Update sensor readings on main screen (called periodically)"""
        try:
            temp_str, humid_str = DHT_SENSOR.read_formatted()
            self.temp_label.config(text=temp_str)
            self.humid_label.config(text=humid_str)
            
            if temp_str == "N/A":
                self.sensor_status.config(
                    text="⚠️ Sensor not connected (check GPIO4 wiring)",
                    fg='#ffaa00'
                )
            else:
                self.sensor_status.config(
                    text="✓ Last updated: " + self.get_current_time(),
                    fg='#00aa00'
                )
        except Exception as e:
            logger.error(f"Sensor update error: {e}")
            self.temp_label.config(text="Error")
            self.humid_label.config(text="Error")
            self.sensor_status.config(
                text="⚠️ Sensor error",
                fg='#ff0000'
            )
        
        # Schedule next update in 5 seconds
        self.root.after(5000, self.update_sensor_readings)
    
    def get_current_time(self):
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
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
