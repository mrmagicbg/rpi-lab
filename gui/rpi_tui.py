#!/usr/bin/env python3
"""
RPI Lab TUI (Text User Interface)
Real-time monitoring via SSH using rich library

Usage:
  python rpi_tui.py [--sensor|--rf|--both]
  
Options:
  --sensor    Show only sensor data (default)
  --rf        Show only RF/TPMS data
  --both      Show both sensor and RF data
"""

import sys
import time
import argparse
import os
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from sensors.bme690 import BME690Sensor

console = Console()


def get_gas_status_text(gas_resistance: Optional[float]) -> tuple[str, str]:
    """Get gas status text and color based on resistance.
    
    Returns:
        Tuple of (status_text, color)
    """
    if gas_resistance is None:
        return "N/A", "white"
    
    gas_kohm = gas_resistance / 1000.0
    
    if gas_resistance < 5000:
        return f"⚠️  Gas Detected ({gas_resistance:.0f} Ω)", "red"
    elif gas_resistance < 10000:
        return f"🔥 Initial Warm-Up ({gas_kohm:.1f} kΩ)", "bright_red"
    elif gas_resistance < 20000:
        return f"⏳ Stabilizing ({gas_kohm:.1f} kΩ)", "yellow"
    elif gas_resistance < 40000:
        return f"📈 Continued Stabilization ({gas_kohm:.1f} kΩ)", "bright_yellow"
    elif gas_resistance < 60000:
        return f"🔄 Further Stabilization ({gas_kohm:.1f} kΩ)", "bright_green"
    elif gas_resistance < 100000:
        return f"✅ Stabilized ({gas_kohm:.1f} kΩ)", "green"
    else:
        return f"✓ Normal Operation ({gas_kohm:.1f} kΩ)", "bright_green"


def create_sensor_panel(sensor: BME690Sensor) -> Panel:
    """Create sensor data panel."""
    h, t, p, g = sensor.read()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="cyan bold")
    table.add_column("Value", style="white bold")
    
    # Temperature
    temp_str = f"{t:.1f} °C" if t is not None else "N/A"
    temp_color = "red" if t and t > 30 else "blue" if t and t < 0 else "green"
    table.add_row("🌡️  Temperature:", Text(temp_str, style=temp_color))
    
    # Humidity
    humid_str = f"{h:.1f} %RH" if h is not None else "N/A"
    humid_color = "yellow" if h and (h < 25 or h > 80) else "cyan"
    table.add_row("💧 Humidity:", Text(humid_str, style=humid_color))
    
    # Pressure
    press_str = f"{p:.1f} hPa" if p is not None else "N/A"
    table.add_row("🌍 Pressure:", Text(press_str, style="magenta"))
    
    # Gas resistance with status
    gas_status, gas_color = get_gas_status_text(g)
    table.add_row("💨 Gas Status:", Text(gas_status, style=gas_color))
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return Panel(
        table,
        title=f"[bold cyan]BME690 Sensor (I2C 0x76)[/bold cyan]",
        subtitle=f"[dim]Updated: {timestamp}[/dim]",
        border_style="cyan"
    )


def create_rf_panel() -> Panel:
    """Create RF/TPMS data panel."""
    table = Table(show_header=True, box=None)
    table.add_column("ID", style="cyan")
    table.add_column("Pressure", style="green")
    table.add_column("Temp", style="yellow")
    table.add_column("Battery", style="magenta")
    table.add_column("RSSI", style="blue")
    table.add_column("Last Seen", style="white")
    
    # Placeholder - would need to read from TPMS decoder state
    table.add_row(
        "[dim]No active sensors[/dim]",
        "-",
        "-",
        "-",
        "-",
        "-"
    )
    
    return Panel(
        table,
        title="[bold yellow]TPMS RF Monitor (433.92 MHz)[/bold yellow]",
        subtitle="[dim]Listening for tire pressure sensors...[/dim]",
        border_style="yellow"
    )


def create_header() -> Panel:
    """Create header panel."""
    header_text = Text()
    header_text.append("RPI Lab ", style="bold cyan")
    header_text.append("TUI Monitor", style="bold white")
    header_text.append(" v3.0.4", style="dim")
    
    return Panel(
        header_text,
        style="bold white on blue",
        padding=(0, 2)
    )


def create_layout(show_sensor: bool, show_rf: bool) -> Layout:
    """Create TUI layout."""
    layout = Layout()
    
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    if show_sensor and show_rf:
        layout["body"].split_row(
            Layout(name="sensor"),
            Layout(name="rf")
        )
    elif show_sensor:
        layout["body"].update(Layout(name="sensor"))
    else:
        layout["body"].update(Layout(name="rf"))
    
    return layout


def main():
    """Main TUI loop."""
    parser = argparse.ArgumentParser(description="RPI Lab TUI Monitor")
    parser.add_argument('--sensor', action='store_true', help='Show sensor data only')
    parser.add_argument('--rf', action='store_true', help='Show RF/TPMS data only')
    parser.add_argument('--both', action='store_true', help='Show both sensor and RF data')
    parser.add_argument('--interval', type=float, default=2.0, help='Update interval in seconds (default: 2.0)')
    args = parser.parse_args()
    
    # Determine what to show
    show_sensor = args.sensor or args.both or (not args.rf and not args.both)
    show_rf = args.rf or args.both
    
    # Initialize sensor
    sensor = BME690Sensor()
    
    if not sensor.available:
        console.print("[red]❌ BME690 sensor not available![/red]")
        console.print("[yellow]Check I2C connection and permissions[/yellow]")
        return 1
    
    console.print("[green]✓ Connected to BME690 sensor[/green]")
    console.print(f"[cyan]Update interval: {args.interval}s[/cyan]")
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")
    
    try:
        with Live(console=console, screen=True, auto_refresh=False) as live:
            while True:
                layout = create_layout(show_sensor, show_rf)
                
                # Update header
                layout["header"].update(create_header())
                
                # Update body
                if show_sensor:
                    if show_rf:
                        layout["body"]["sensor"].update(create_sensor_panel(sensor))
                        layout["body"]["rf"].update(create_rf_panel())
                    else:
                        layout["body"].update(create_sensor_panel(sensor))
                else:
                    layout["body"].update(create_rf_panel())
                
                # Update footer
                footer_text = Text()
                footer_text.append("Press ", style="dim")
                footer_text.append("Ctrl+C", style="bold red")
                footer_text.append(" to exit", style="dim")
                footer_text.append(" | Refreshing every ", style="dim")
                footer_text.append(f"{args.interval}s", style="bold cyan")
                
                layout["footer"].update(Panel(footer_text, style="dim"))
                
                live.update(layout)
                live.refresh()
                time.sleep(args.interval)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]✓ TUI Monitor stopped[/yellow]")
        return 0
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
