#!/usr/bin/env python3
"""
TPMS Data Logging Module

Provides CSV and JSON export for TPMS sensor readings with session management.
"""

import csv
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from tpms_decoder import TPMSReading

logger = logging.getLogger(__name__)


class TPMSLogger:
    """Handles logging of TPMS sensor readings to CSV and JSON formats"""
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize TPMS logger
        
        Args:
            log_dir: Directory to store log files. Defaults to ~/rpi-lab/logs/tpms/
        """
        if not log_dir:
            log_dir = os.path.expanduser("~/rpi-lab/logs/tpms")
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session-based filenames
        session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = f"tpms_session_{session_time}"
        
        self.csv_file = self.log_dir / f"{self.session_name}.csv"
        self.json_file = self.log_dir / f"{self.session_name}.json"
        
        self.readings: List[TPMSReading] = []
        self.csv_written = False
        
        logger.info(f"TPMS Logger initialized: {self.log_dir}")
    
    def add_reading(self, reading: TPMSReading) -> None:
        """Add a TPMS reading to the session log"""
        self.readings.append(reading)
    
    def add_readings(self, readings: List[TPMSReading]) -> None:
        """Add multiple TPMS readings"""
        self.readings.extend(readings)
    
    def write_csv(self, overwrite: bool = True) -> Path:
        """
        Write all readings to CSV file
        
        Args:
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to CSV file
        """
        if not overwrite and self.csv_file.exists():
            logger.warning(f"CSV file exists, skipping: {self.csv_file}")
            return self.csv_file
        
        if not self.readings:
            logger.warning("No readings to write")
            return self.csv_file
        
        try:
            with open(self.csv_file, 'w', newline='') as f:
                fieldnames = [
                    'timestamp', 'sensor_id', 'pressure_psi', 'pressure_kpa',
                    'temperature_c', 'temperature_f', 'battery_low',
                    'rssi', 'lqi', 'protocol', 'supplier', 'pressure_status'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for reading in self.readings:
                    temp_f = reading.temperature_c * 9/5 + 32 if reading.temperature_c else None
                    row = {
                        'timestamp': reading.timestamp,
                        'sensor_id': reading.sensor_id,
                        'pressure_psi': f"{reading.pressure_psi:.2f}" if reading.pressure_psi else "",
                        'pressure_kpa': f"{reading.pressure_kpa:.2f}" if reading.pressure_kpa else "",
                        'temperature_c': f"{reading.temperature_c:.1f}" if reading.temperature_c else "",
                        'temperature_f': f"{temp_f:.1f}" if temp_f else "",
                        'battery_low': reading.battery_low,
                        'rssi': reading.signal_strength,
                        'lqi': reading.link_quality,
                        'protocol': reading.protocol,
                        'supplier': reading.supplier or "",
                        'pressure_status': reading.get_pressure_status()
                    }
                    writer.writerow(row)
            
            logger.info(f"CSV log written: {self.csv_file} ({len(self.readings)} readings)")
            self.csv_written = True
            return self.csv_file
        
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")
            raise
    
    def write_json(self, overwrite: bool = True) -> Path:
        """
        Write all readings to JSON file
        
        Args:
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to JSON file
        """
        if not overwrite and self.json_file.exists():
            logger.warning(f"JSON file exists, skipping: {self.json_file}")
            return self.json_file
        
        if not self.readings:
            logger.warning("No readings to write")
            return self.json_file
        
        try:
            data = {
                'session': self.session_name,
                'created': datetime.now().isoformat(),
                'reading_count': len(self.readings),
                'readings': [reading.to_dict() for reading in self.readings],
                'summary': self._generate_summary()
            }
            
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"JSON log written: {self.json_file}")
            return self.json_file
        
        except Exception as e:
            logger.error(f"Failed to write JSON: {e}")
            raise
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics for the session"""
        if not self.readings:
            return {}
        
        summary = {
            'total_readings': len(self.readings),
            'unique_sensors': len(set(r.sensor_id for r in self.readings)),
            'protocols_detected': list(set(r.protocol for r in self.readings)),
            'suppliers_detected': list(set(r.supplier for r in self.readings if r.supplier)),
            'low_battery_count': sum(1 for r in self.readings if r.battery_low),
            'low_pressure_count': sum(1 for r in self.readings if r.get_pressure_status() in ['LOW', 'CRITICAL']),
            'high_pressure_count': sum(1 for r in self.readings if r.get_pressure_status() == 'HIGH'),
            'avg_rssi': round(sum(r.signal_strength for r in self.readings if r.signal_strength) / 
                            sum(1 for r in self.readings if r.signal_strength), 1) if any(r.signal_strength for r in self.readings) else None,
        }
        
        # Pressure statistics
        pressures = [r.pressure_psi for r in self.readings if r.pressure_psi]
        if pressures:
            summary['pressure_stats'] = {
                'min_psi': min(pressures),
                'max_psi': max(pressures),
                'avg_psi': round(sum(pressures) / len(pressures), 2)
            }
        
        # Temperature statistics
        temps = [r.temperature_c for r in self.readings if r.temperature_c is not None]
        if temps:
            summary['temperature_stats'] = {
                'min_c': min(temps),
                'max_c': max(temps),
                'avg_c': round(sum(temps) / len(temps), 1)
            }
        
        return summary
    
    def export_all(self) -> Dict[str, Path]:
        """Export to both CSV and JSON formats"""
        return {
            'csv': self.write_csv(),
            'json': self.write_json()
        }
    
    def get_summary(self) -> Dict:
        """Get summary of current session"""
        return {
            'session_name': self.session_name,
            'reading_count': len(self.readings),
            'unique_sensors': len(set(r.sensor_id for r in self.readings)),
            'csv_file': str(self.csv_file),
            'json_file': str(self.json_file),
            'log_dir': str(self.log_dir)
        }


def analyze_log_file(filepath: str) -> Dict:
    """
    Analyze a saved TPMS log file (CSV or JSON)
    
    Args:
        filepath: Path to log file
        
    Returns:
        Dictionary with analysis results
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")
    
    if filepath.suffix == '.csv':
        return _analyze_csv(filepath)
    elif filepath.suffix == '.json':
        return _analyze_json(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


def _analyze_csv(filepath: Path) -> Dict:
    """Analyze CSV log file"""
    readings = []
    
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                readings.append(row)
        
        if not readings:
            return {'error': 'No data in CSV file'}
        
        # Parse numeric values
        pressures = []
        temps = []
        rssis = []
        sensor_ids = set()
        protocols = set()
        
        for row in readings:
            sensor_ids.add(row.get('sensor_id', ''))
            protocols.add(row.get('protocol', ''))
            
            try:
                if row.get('pressure_psi'):
                    pressures.append(float(row['pressure_psi']))
                if row.get('temperature_c'):
                    temps.append(float(row['temperature_c']))
                if row.get('rssi'):
                    rssis.append(int(row['rssi']))
            except ValueError:
                continue
        
        return {
            'file': str(filepath),
            'total_readings': len(readings),
            'unique_sensors': len(sensor_ids),
            'protocols': list(protocols),
            'pressure_stats': {
                'min': min(pressures) if pressures else None,
                'max': max(pressures) if pressures else None,
                'avg': round(sum(pressures) / len(pressures), 2) if pressures else None
            },
            'temperature_stats': {
                'min': min(temps) if temps else None,
                'max': max(temps) if temps else None,
                'avg': round(sum(temps) / len(temps), 1) if temps else None
            },
            'signal_stats': {
                'avg_rssi': round(sum(rssis) / len(rssis), 1) if rssis else None
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze CSV: {e}")
        return {'error': str(e)}


def _analyze_json(filepath: Path) -> Dict:
    """Analyze JSON log file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Return the summary if available
        return {
            'file': str(filepath),
            'session': data.get('session'),
            'created': data.get('created'),
            'summary': data.get('summary', {})
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze JSON: {e}")
        return {'error': str(e)}


if __name__ == '__main__':
    # Test logger
    logging.basicConfig(level=logging.INFO)
    
    logger = TPMSLogger()
    
    # Add sample readings
    from tpms_decoder import TPMSReading
    
    sample = TPMSReading(
        sensor_id="12345678",
        pressure_psi=32.5,
        temperature_c=45.2,
        battery_low=False,
        signal_strength=-72,
        protocol="Schrader",
        supplier="Schrader Electronics"
    )
    
    logger.add_reading(sample)
    logger.export_all()
    
    print("✓ Test export complete")
    print(logger.get_summary())
