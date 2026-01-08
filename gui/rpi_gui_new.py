#!/usr/bin/env python3
"""
Enhanced RPI GUI launcher with:
- RF tools, sensor monitoring, and system actions
- Network information display (IP, mask, gateway, DNS)
- BME690 environmental sensor (temperature, humidity, pressure, gas)
- PWM speaker alerts for sensor thresholds
- Large touch-friendly buttons for 800x480 Waveshare 4.3" DSI display

Alert conditions:
- Gas: Beep every 15 seconds when volatile gases detected (low resistance)
- Temperature: Beep hourly when < 0°C or > 30°C
- Humidity: Beep hourly when < 25% or > 80%
- System events: Beep on startup, shutdown, reboot

Requirements:
- tkinter (python3-tk)
- evdev (for touch device detection)
- BME690 sensor (sensors/bme690.py)
- PWM Speaker (sensors/speaker.py)
- RPi.GPIO (for speaker PWM control)
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime, timedelta
import socket
import struct
import fcntl

# Import sensor modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sensors.bme690 import BME690Sensor
from sensors.speaker import get_speaker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rpi_gui')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RF_SCRIPT_PATH = os.path.join(BASE_DIR, 'rf', 'setup_pi.sh')

# Initialize BME690 sensor (I2C 0x76 by default)
BME_SENSOR = BME690Sensor()

# Initialize speaker
SPEAKER = get_speaker()


class NetworkInfo:
    """Network information retrieval."""

    @staticmethod
    def get_ip_address(ifname='eth0'):
        """Get IP address for network interface."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode('utf-8'))
            )[20:24])
            return ip
        except Exception:
            # Try wlan0 if eth0 fails
            if ifname == 'eth0':
                return NetworkInfo.get_ip_address('wlan0')
            return 'N/A'

    @staticmethod
    def get_netmask(ifname='eth0'):
        """Get netmask for network interface and return in CIDR notation."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            netmask = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x891b,  # SIOCGIFNETMASK
                struct.pack('256s', ifname[:15].encode('utf-8'))
            )[20:24])
            # Convert netmask to CIDR notation
            cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
            return f"/{cidr}"
        except Exception:
            if ifname == 'eth0':
                return NetworkInfo.get_netmask('wlan0')
            return '/N/A'

    @staticmethod
    def get_gateway():
        """Get default gateway."""
        try:
            with open("/proc/net/route") as fh:
                for line in fh:
                    fields = line.strip().split()
                    if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                        continue
                    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
        except Exception:
            pass
        return 'N/A'

    @staticmethod
    def get_dns_servers():
        """Get DNS servers from resolv.conf."""
        dns_servers = []
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns = line.split()[1]
                        dns_servers.append(dns)
        except Exception:
            pass
        return dns_servers if dns_servers else ['N/A']


class RPILauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RPI Lab - Control Panel")
        
        # Error tracking for sensor updates with exponential backoff
        self.sensor_error_count = 0
        self.update_interval = 5000  # Initial update interval in milliseconds
        
        # Alert tracking
        self.last_gas_alert = None
        self.last_temp_alert = None
        self.last_humidity_alert = None
        self.gas_alert_interval = 15  # seconds
        self.hourly_alert_interval = 3600  # seconds (1 hour)
        
        # Threshold values
        self.temp_min = 0.0
        self.temp_max = 30.0
        self.humidity_min = 25.0
        self.humidity_max = 80.0
        self.gas_threshold = 50000  # Ohms - low resistance indicates volatile gases
        
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
        
        # Info display area (network + sensor in horizontal layout)
        info_frame = tk.Frame(main_frame, bg='#1e1e1e')
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # Network information (left side)
        self.network_frame = tk.Frame(info_frame, bg='#2d2d2d', relief='raised', bd=3)
        self.network_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        net_title = tk.Label(
            self.network_frame,
            text="🌐 Network Info",
            font=('Arial', 12, 'bold'),
            fg='#00ff88',
            bg='#2d2d2d',
            pady=5
        )
        net_title.pack()
        
        # Network data labels
        self.net_ip_label = tk.Label(
            self.network_frame,
            text="IP: Loading...",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#2d2d2d',
            anchor='w',
            justify='left'
        )
        self.net_ip_label.pack(padx=10, anchor='w')
        
        self.net_gateway_label = tk.Label(
            self.network_frame,
            text="GW: Loading...",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#2d2d2d',
            anchor='w',
            justify='left'
        )
        self.net_gateway_label.pack(padx=10, anchor='w')
        
        self.net_dns_label = tk.Label(
            self.network_frame,
            text="DNS: Loading...",
            font=('Arial', 10),
            fg='#ffffff',
            bg='#2d2d2d',
            anchor='w',
            justify='left',
            wraplength=300
        )
        self.net_dns_label.pack(padx=10, anchor='w', pady=(0, 5))
        
        # Sensor display area (right side)
        self.sensor_frame = tk.Frame(info_frame, bg='#2d2d2d', relief='raised', bd=3)
        self.sensor_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        sensor_title = tk.Label(
            self.sensor_frame,
            text="🌡️ BME690 Sensor (I2C)",
            font=('Arial', 12, 'bold'),
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
        temp_container.grid(row=0, column=0, padx=10, pady=2)
        
        tk.Label(
            temp_container,
            text="Temp:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(side='left')
        
        self.temp_label = tk.Label(
            temp_container,
            text="--°C",
            font=('Arial', 14, 'bold'),
            fg='#ff6b6b',
            bg='#2d2d2d'
        )
        self.temp_label.pack(side='left', padx=5)
        
        # Humidity display
        humid_container = tk.Frame(sensor_data_frame, bg='#2d2d2d')
        humid_container.grid(row=0, column=1, padx=10, pady=2)
        
        tk.Label(
            humid_container,
            text="Humid:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(side='left')
        
        self.humid_label = tk.Label(
            humid_container,
            text="--%",
            font=('Arial', 14, 'bold'),
            fg='#4ecdc4',
            bg='#2d2d2d'
        )
        self.humid_label.pack(side='left', padx=5)

        # Pressure display
        press_container = tk.Frame(sensor_data_frame, bg='#2d2d2d')
        press_container.grid(row=1, column=0, padx=10, pady=2)

        tk.Label(
            press_container,
            text="Press:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(side='left')

        self.press_label = tk.Label(
            press_container,
            text="-- hPa",
            font=('Arial', 14, 'bold'),
            fg='#9aa0ff',
            bg='#2d2d2d'
        )
        self.press_label.pack(side='left', padx=5)

        # Gas resistance display
        gas_container = tk.Frame(sensor_data_frame, bg='#2d2d2d')
        gas_container.grid(row=1, column=1, padx=10, pady=2)

        tk.Label(
            gas_container,
            text="Gas:",
            font=('Arial', 10, 'bold'),
            fg='#ffffff',
            bg='#2d2d2d'
        ).pack(side='left')

        self.gas_label = tk.Label(
            gas_container,
            text="-- Ω",
            font=('Arial', 14, 'bold'),
            fg='#ffae00',
            bg='#2d2d2d'
        )
        self.gas_label.pack(side='left', padx=5)
        
        # Status label
        self.sensor_status = tk.Label(
            self.sensor_frame,
            text="Initializing sensor...",
            font=('Arial', 8),
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
            'font': ('Arial', 16, 'bold'),
            'width': 22,
            'height': 1,
            'relief': 'raised',
            'bd': 4,
            'fg': 'white'
        }
        
        # Menu buttons - all uniform size
        btn_rf = tk.Button(
            button_frame,
            text="📡 TPMS Monitor",
            command=self.run_rf_script,
            bg='#2d89ef',
            activebackground='#1e5fa8',
            **button_config
        )
        btn_rf.pack(pady=3, fill='x')
        
        btn_test_beep = tk.Button(
            button_frame,
            text="🔊 Test Speaker",
            command=self.test_beep,
            bg='#f7630c',
            activebackground='#c4500a',
            **button_config
        )
        btn_test_beep.pack(pady=3, fill='x')
        
        btn_reboot = tk.Button(
            button_frame,
            text="🔄 Reboot System",
            command=self.reboot_pi,
            bg='#e81123',
            activebackground='#a50011',
            **button_config
        )
        btn_reboot.pack(pady=3, fill='x')
        
        btn_shell = tk.Button(
            button_frame,
            text="💻 Open Terminal",
            command=self.open_shell,
            bg='#00a300',
            activebackground='#007000',
            **button_config
        )
        btn_shell.pack(pady=3, fill='x')
        
        btn_exit = tk.Button(
            button_frame,
            text="❌ Exit to Desktop",
            command=self.exit_app,
            bg='#555555',
            activebackground='#333333',
            **button_config
        )
        btn_exit.pack(pady=3, fill='x')
        
        # Footer with instructions
        footer = tk.Label(
            self.root,
            text="Touch buttons to perform actions • F11: fullscreen • ESC: exit",
            font=('Arial', 8),
            fg='#666666',
            bg='#1e1e1e',
            pady=3
        )
        footer.pack(side='bottom')
        
        # Keyboard shortcuts
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', lambda e: self.exit_app())
        
        # Start update loops
        self.update_network_info()
        self.update_sensor_readings()
        
        # Play startup beep
        if SPEAKER.available:
            SPEAKER.beep_startup()
        
        logger.info("GUI initialized successfully")
    
    def update_network_info(self):
        """Update network information display."""
        try:
            ip = NetworkInfo.get_ip_address()
            mask = NetworkInfo.get_netmask()
            gateway = NetworkInfo.get_gateway()
            dns_servers = NetworkInfo.get_dns_servers()
            
            self.net_ip_label.config(text=f"IP: {ip}{mask}")
            self.net_gateway_label.config(text=f"GW: {gateway}")
            dns_text = "DNS: " + ", ".join(dns_servers[:2])  # Show first 2 DNS servers
            self.net_dns_label.config(text=dns_text)
        except Exception as e:
            logger.error(f"Network info update error: {e}")
        
        # Update network info every 30 seconds
        self.root.after(30000, self.update_network_info)
    
    def check_sensor_alerts(self, h, t, p, g):
        """Check sensor values and trigger alerts if thresholds exceeded."""
        current_time = datetime.now()
        
        # Gas alert - beep every 15 seconds if volatile gases detected
        if g is not None and g < self.gas_threshold:
            if self.last_gas_alert is None or \
               (current_time - self.last_gas_alert).total_seconds() >= self.gas_alert_interval:
                logger.warning(f"Gas alert! Resistance: {g:.0f} Ω (threshold: {self.gas_threshold} Ω)")
                if SPEAKER.available:
                    SPEAKER.beep_gas_alert()
                self.last_gas_alert = current_time
        
        # Temperature alert - beep hourly if out of range
        if t is not None and (t < self.temp_min or t > self.temp_max):
            if self.last_temp_alert is None or \
               (current_time - self.last_temp_alert).total_seconds() >= self.hourly_alert_interval:
                logger.warning(f"Temperature alert! {t:.1f}°C (range: {self.temp_min}-{self.temp_max}°C)")
                if SPEAKER.available:
                    SPEAKER.beep_temp_alert()
                self.last_temp_alert = current_time
        
        # Humidity alert - beep hourly if out of range
        if h is not None and (h < self.humidity_min or h > self.humidity_max):
            if self.last_humidity_alert is None or \
               (current_time - self.last_humidity_alert).total_seconds() >= self.hourly_alert_interval:
                logger.warning(f"Humidity alert! {h:.1f}% (range: {self.humidity_min}-{self.humidity_max}%)")
                if SPEAKER.available:
                    SPEAKER.beep_humidity_alert()
                self.last_humidity_alert = current_time
    
    def update_sensor_readings(self):
        """Update sensor readings on main screen with error recovery and alert monitoring."""
        try:
            h, t, p, g = BME_SENSOR.read()
            data = BME_SENSOR.read_formatted()
            
            self.temp_label.config(text=data["temperature_str"]) 
            self.humid_label.config(text=data["humidity_str"]) 
            self.press_label.config(text=data["pressure_str"]) 
            self.gas_label.config(text=data["gas_res_str"]) 

            if data["temperature_str"] == "N/A":
                # Sensor not responding - increment error counter
                self.sensor_error_count += 1
                
                # Adjust update interval based on error frequency
                if self.sensor_error_count < 3:
                    self.update_interval = 5000  # 5 sec - normal
                elif self.sensor_error_count < 6:
                    self.update_interval = 15000  # 15 sec - slowing down
                else:
                    self.update_interval = 60000  # 60 sec - very slow
                
                self.sensor_status.config(
                    text=f"⚠️ Sensor not connected (error #{self.sensor_error_count}, retry in {self.update_interval//1000}s)",
                    fg='#ffaa00'
                )
            else:
                # Success - reset error counter and interval
                if self.sensor_error_count > 0:
                    logger.info(f"Sensor recovered after {self.sensor_error_count} errors")
                
                self.sensor_error_count = 0
                self.update_interval = 5000  # Reset to normal interval
                
                status_text = "✓ Last updated: " + self.get_current_time()
                if data.get("heat_stable"):
                    status_text += " • Gas heater stable"
                self.sensor_status.config(
                    text=status_text,
                    fg='#00aa00'
                )
                
                # Check for alert conditions
                self.check_sensor_alerts(h, t, p, g)
                
        except Exception as e:
            logger.error(f"Sensor update error: {e}", exc_info=True)
            self.sensor_error_count += 1
            
            # Exponential backoff based on consecutive errors
            if self.sensor_error_count < 3:
                self.update_interval = 5000  # 5 sec
            elif self.sensor_error_count < 6:
                self.update_interval = 15000  # 15 sec
            else:
                self.update_interval = 60000  # 60 sec
            
            # Show error state with countdown
            self.temp_label.config(text="Error")
            self.humid_label.config(text="Error")
            self.press_label.config(text="Error")
            self.gas_label.config(text="Error")
            self.sensor_status.config(
                text=f"⚠️ Sensor error #{self.sensor_error_count} ({e.__class__.__name__}). Retry in {self.update_interval//1000}s",
                fg='#ff6666'
            )
        
        # Schedule next update with current interval (may have changed due to errors)
        self.root.after(self.update_interval, self.update_sensor_readings)
    
    def get_current_time(self):
        """Get current time string."""
        return datetime.now().strftime("%H:%M:%S")
    
    def run_rf_script(self):
        """Launch TPMS RF Monitor GUI."""
        logger.info("RF Monitor button pressed")
        
        try:
            # Launch TPMS monitor in new window
            rf_dir = os.path.join(BASE_DIR, 'rf')
            tpms_gui_path = os.path.join(rf_dir, 'tpms_monitor_gui.py')
            
            if not os.path.isfile(tpms_gui_path):
                logger.error(f"TPMS monitor not found: {tpms_gui_path}")
                messagebox.showerror(
                    "TPMS Monitor Not Found",
                    f"TPMS monitor GUI not found at:\n{tpms_gui_path}"
                )
                return
            
            # Launch TPMS monitor as standalone window
            logger.info(f"Launching TPMS monitor: {tpms_gui_path}")
            venv_python = os.path.join(BASE_DIR, '.venv', 'bin', 'python')
            
            if os.path.exists(venv_python):
                subprocess.Popen([venv_python, tpms_gui_path])
            else:
                subprocess.Popen(['python3', tpms_gui_path])
            
        except Exception as e:
            logger.error(f"Failed to launch TPMS monitor: {e}")
            messagebox.showerror("Error", f"Failed to launch TPMS monitor:\n{e}")
    
    def test_beep(self):
        """Play test beep pattern."""
        logger.info("Test beep button pressed")
        if SPEAKER.available:
            SPEAKER.test_beep()
        else:
            messagebox.showwarning("Speaker Not Available", 
                                   "Speaker hardware not initialized.\n"
                                   "Ensure GPIO pin 12 is properly wired.")
    
    def reboot_pi(self):
        """Reboot the Raspberry Pi after confirmation."""
        logger.info("Reboot button pressed")
        if messagebox.askyesno("Confirm Reboot", "Reboot Raspberry Pi now?"):
            logger.info("Reboot confirmed")
            if SPEAKER.available:
                SPEAKER.beep_reboot()
            try:
                subprocess.Popen(['sudo', 'reboot'])
            except Exception as e:
                logger.error(f"Failed to reboot: {e}")
                messagebox.showerror("Error", f"Failed to reboot:\n{e}")
    
    def open_shell(self):
        """Open a terminal window."""
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
        """Exit the application."""
        logger.info("Exit button pressed")
        if messagebox.askyesno("Confirm Exit", "Exit RPI Lab GUI?"):
            logger.info("Exit confirmed")
            if SPEAKER.available:
                SPEAKER.beep_shutdown()
            try:
                self.root.destroy()
            finally:
                sys.exit(0)
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
        logger.info(f"Fullscreen: {not current}")


def main():
    """Main entry point."""
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
        if SPEAKER.available:
            SPEAKER.cleanup()


if __name__ == '__main__':
    main()
