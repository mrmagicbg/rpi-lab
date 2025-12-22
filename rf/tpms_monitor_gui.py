#!/usr/bin/env python3
"""
RF Data Visualization GUI for TPMS Monitoring

Live display of TPMS sensor readings from CC1101 radio captures.
Shows tire pressure, temperature, battery status, and signal quality
for multiple sensors.
"""

import os
import sys
import subprocess
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Dict, Optional
import logging

# Import TPMS decoder
sys.path.insert(0, os.path.dirname(__file__))
from tpms_decoder import TPMSDecoder, TPMSReading

logger = logging.getLogger(__name__)


class TPMSMonitorGUI:
    """GUI for monitoring TPMS sensors in real-time"""
    
    def __init__(self, root: tk.Tk, standalone: bool = True):
        self.root = root
        self.standalone = standalone
        self.decoder = TPMSDecoder()
        self.sensors: Dict[str, TPMSReading] = {}  # sensor_id -> latest reading
        self.packet_queue = queue.Queue()
        self.is_monitoring = False
        self.rx_process: Optional[subprocess.Popen] = None
        
        if standalone:
            self.root.title("TPMS Monitor - RF Capture")
            self.root.geometry("900x700")
        
        self._setup_ui()
        
        # Start packet processor thread
        self.processor_thread = threading.Thread(target=self._process_packets, daemon=True)
        self.processor_thread.start()
        
        logger.info("TPMS Monitor GUI initialized")
    
    def _setup_ui(self):
        """Create the GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(
            main_frame,
            text="🔬 TPMS RF Monitor",
            font=('Arial', 20, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e'
        )
        title.pack(pady=(0, 10))
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=2)
        control_frame.pack(fill='x', pady=5)
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶️ Start Capture",
            command=self.start_capture,
            font=('Arial', 12, 'bold'),
            bg='#00a300',
            fg='white',
            padx=20,
            pady=10
        )
        self.start_btn.pack(side='left', padx=10, pady=10)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹️ Stop Capture",
            command=self.stop_capture,
            font=('Arial', 12, 'bold'),
            bg='#e81123',
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=10, pady=10)
        
        self.status_label = tk.Label(
            control_frame,
            text="⏸️ Stopped",
            font=('Arial', 12),
            fg='#999999',
            bg='#2d2d2d'
        )
        self.status_label.pack(side='left', padx=20)
        
        # Stats
        self.stats_label = tk.Label(
            control_frame,
            text="Packets: 0 | Sensors: 0",
            font=('Arial', 10),
            fg='#666666',
            bg='#2d2d2d'
        )
        self.stats_label.pack(side='right', padx=10)
        
        # Sensor display area (scrollable)
        sensor_container = tk.Frame(main_frame, bg='#1e1e1e')
        sensor_container.pack(fill='both', expand=True, pady=10)
        
        canvas = tk.Canvas(sensor_container, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(sensor_container, orient='vertical', command=canvas.yview)
        self.sensor_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        self.sensor_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.sensor_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Log area
        log_frame = tk.LabelFrame(
            main_frame,
            text="Activity Log",
            font=('Arial', 10, 'bold'),
            fg='#00ff88',
            bg='#1e1e1e'
        )
        log_frame.pack(fill='both', pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=('Courier', 9),
            bg='#0a0a0a',
            fg='#00ff00',
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Close button (only in standalone mode)
        if self.standalone:
            close_btn = tk.Button(
                main_frame,
                text="❌ Close",
                command=self.close_window,
                font=('Arial', 12),
                bg='#555555',
                fg='white',
                padx=20,
                pady=5
            )
            close_btn.pack(pady=5)
    
    def log(self, message: str, level: str = "INFO"):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {level}: {message}\n")
        self.log_text.see('end')
        logger.info(message)
    
    def start_capture(self):
        """Start RF capture with rx_profile_demo"""
        if self.is_monitoring:
            return
        
        # Find rx_profile_demo binary
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        rx_binary = os.path.join(base_dir, 'rf', 'CC1101', 'rx_profile_demo')
        
        if not os.path.exists(rx_binary):
            self.log("ERROR: rx_profile_demo not found! Build it first.", "ERROR")
            messagebox.showerror(
                "Binary Not Found",
                f"RF tool not compiled!\n\nRun: sudo bash /opt/rpi-lab/install/install_rf.sh\n\nExpected at: {rx_binary}"
            )
            return
        
        self.log("Starting TPMS capture (433.92 MHz, mode TPMS)...", "INFO")
        
        try:
            # Start rx_profile_demo in TPMS mode
            self.rx_process = subprocess.Popen(
                ['sudo', rx_binary, '-mTPMS'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start reader thread
            self.is_monitoring = True
            reader_thread = threading.Thread(target=self._read_rx_output, daemon=True)
            reader_thread.start()
            
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="📡 Monitoring...", fg='#00ff00')
            self.log("Capture started. Listening for TPMS sensors...", "INFO")
            
        except Exception as e:
            self.log(f"Failed to start capture: {e}", "ERROR")
            messagebox.showerror("Start Failed", f"Failed to start RF capture:\n{e}")
    
    def stop_capture(self):
        """Stop RF capture"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.rx_process:
            try:
                self.rx_process.terminate()
                self.rx_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.rx_process.kill()
            self.rx_process = None
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="⏸️ Stopped", fg='#999999')
        self.log("Capture stopped.", "INFO")
    
    def _read_rx_output(self):
        """Read output from rx_profile_demo process"""
        if not self.rx_process:
            return
        
        try:
            for line in iter(self.rx_process.stdout.readline, ''):
                if not self.is_monitoring:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse rx_profile_demo output
                # Format: timestamp MODE=0x07 LEN=10 RSSI=-50 LQI=100 HEX=... DECODE=... fields
                if 'HEX=' in line and 'RSSI=' in line:
                    self._parse_rx_line(line)
        except Exception as e:
            logger.error(f"RX reader error: {e}")
        finally:
            self.is_monitoring = False
    
    def _parse_rx_line(self, line: str):
        """Parse a line from rx_profile_demo output"""
        try:
            # Extract fields
            parts = line.split()
            hex_data = None
            rssi = 0
            lqi = 0
            
            for part in parts:
                if part.startswith('HEX='):
                    hex_data = part.split('=')[1]
                elif part.startswith('RSSI='):
                    rssi = int(part.split('=')[1])
                elif part.startswith('LQI='):
                    lqi = int(part.split('=')[1])
            
            if hex_data:
                raw_bytes = bytes.fromhex(hex_data)
                self.packet_queue.put((raw_bytes, rssi, lqi))
        except Exception as e:
            logger.debug(f"Failed to parse RX line: {e}")
    
    def _process_packets(self):
        """Process packets from queue and update GUI"""
        packet_count = 0
        
        while True:
            try:
                raw_bytes, rssi, lqi = self.packet_queue.get(timeout=0.1)
                packet_count += 1
                
                # Decode packet
                reading = self.decoder.decode_packet(raw_bytes, rssi, lqi)
                
                if reading and reading.sensor_id != "UNKNOWN":
                    # Update or add sensor
                    self.sensors[reading.sensor_id] = reading
                    self.root.after(0, self._update_sensor_display)
                    self.root.after(0, lambda: self.log(
                        f"Sensor {reading.sensor_id}: {reading.pressure_psi:.1f} PSI, "
                        f"{reading.temperature_c:.1f}°C [{reading.protocol}]"
                    ))
                else:
                    self.root.after(0, lambda: self.log(
                        f"Unknown packet: {raw_bytes.hex()[:20]}...", "DEBUG"
                    ))
                
                # Update stats
                self.root.after(0, lambda: self.stats_label.config(
                    text=f"Packets: {packet_count} | Sensors: {len(self.sensors)}"
                ))
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Packet processing error: {e}")
    
    def _update_sensor_display(self):
        """Update sensor cards in GUI"""
        # Clear existing cards
        for widget in self.sensor_frame.winfo_children():
            widget.destroy()
        
        if not self.sensors:
            no_data = tk.Label(
                self.sensor_frame,
                text="⏳ Waiting for TPMS sensors...\n\nMake sure CC1101 is connected and configured for 433.92 MHz.",
                font=('Arial', 12),
                fg='#666666',
                bg='#1e1e1e',
                pady=50
            )
            no_data.pack()
            return
        
        # Create card for each sensor
        for sensor_id, reading in sorted(self.sensors.items()):
            self._create_sensor_card(sensor_id, reading)
    
    def _create_sensor_card(self, sensor_id: str, reading: TPMSReading):
        """Create a display card for one sensor"""
        card = tk.Frame(self.sensor_frame, bg='#2d2d2d', relief='raised', bd=3)
        card.pack(fill='x', padx=10, pady=5)
        
        # Header
        header = tk.Frame(card, bg='#1e5fa8')
        header.pack(fill='x')
        
        tk.Label(
            header,
            text=f"🚗 Sensor: {sensor_id}",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#1e5fa8',
            padx=10,
            pady=5
        ).pack(side='left')
        
        tk.Label(
            header,
            text=f"{reading.protocol}",
            font=('Arial', 10),
            fg='#cccccc',
            bg='#1e5fa8',
            padx=10
        ).pack(side='right')
        
        # Data grid
        data_frame = tk.Frame(card, bg='#2d2d2d')
        data_frame.pack(fill='x', padx=15, pady=10)
        
        # Pressure
        if reading.pressure_psi:
            pressure_frame = tk.Frame(data_frame, bg='#2d2d2d')
            pressure_frame.pack(side='left', padx=20)
            
            tk.Label(
                pressure_frame,
                text="🔵 PRESSURE",
                font=('Arial', 9),
                fg='#888888',
                bg='#2d2d2d'
            ).pack()
            
            tk.Label(
                pressure_frame,
                text=f"{reading.pressure_psi:.1f} PSI",
                font=('Arial', 18, 'bold'),
                fg='#4ecdc4',
                bg='#2d2d2d'
            ).pack()
            
            tk.Label(
                pressure_frame,
                text=f"({reading.pressure_kpa:.0f} kPa)",
                font=('Arial', 9),
                fg='#666666',
                bg='#2d2d2d'
            ).pack()
        
        # Temperature
        if reading.temperature_c is not None:
            temp_frame = tk.Frame(data_frame, bg='#2d2d2d')
            temp_frame.pack(side='left', padx=20)
            
            tk.Label(
                temp_frame,
                text="🌡️ TEMPERATURE",
                font=('Arial', 9),
                fg='#888888',
                bg='#2d2d2d'
            ).pack()
            
            temp_f = reading.temperature_c * 9/5 + 32
            tk.Label(
                temp_frame,
                text=f"{reading.temperature_c:.1f}°C",
                font=('Arial', 18, 'bold'),
                fg='#ff6b6b',
                bg='#2d2d2d'
            ).pack()
            
            tk.Label(
                temp_frame,
                text=f"({temp_f:.1f}°F)",
                font=('Arial', 9),
                fg='#666666',
                bg='#2d2d2d'
            ).pack()
        
        # Battery & Signal
        info_frame = tk.Frame(data_frame, bg='#2d2d2d')
        info_frame.pack(side='left', padx=20)
        
        if reading.battery_low is not None:
            battery_color = '#ff0000' if reading.battery_low else '#00ff00'
            battery_text = 'LOW ⚠️' if reading.battery_low else 'OK ✓'
            tk.Label(
                info_frame,
                text=f"🔋 Battery: {battery_text}",
                font=('Arial', 10),
                fg=battery_color,
                bg='#2d2d2d'
            ).pack()
        
        if reading.signal_strength:
            tk.Label(
                info_frame,
                text=f"📶 RSSI: {reading.signal_strength} dBm",
                font=('Arial', 9),
                fg='#888888',
                bg='#2d2d2d'
            ).pack()
        
        # Timestamp
        tk.Label(
            card,
            text=f"Last seen: {reading.timestamp}",
            font=('Arial', 8),
            fg='#555555',
            bg='#2d2d2d',
            pady=5
        ).pack()
    
    def close_window(self):
        """Close the window"""
        self.stop_capture()
        if self.standalone:
            self.root.destroy()
        else:
            self.root.quit()


def main():
    """Standalone launcher"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    root = tk.Tk()
    app = TPMSMonitorGUI(root, standalone=True)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.stop_capture()


if __name__ == '__main__':
    main()
