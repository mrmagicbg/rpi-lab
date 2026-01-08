#!/usr/bin/env python3
"""
TPMS (Tire Pressure Monitoring System) Decoder Module

Supports decoding of TPMS sensor data from common protocols:
- Schrader (EG53MA4, G4, etc.) - 315MHz/433MHz
- Siemens/VDO (Continental) - 433MHz
- Generic Manchester-encoded TPMS frames

Typical TPMS packet structure:
- Preamble (sync bits)
- Sensor ID (32 bits / 4 bytes)
- Pressure (8-16 bits, usually kPa or PSI * 4)
- Temperature (8 bits, usually °C + offset)
- Battery status (2-4 bits)
- Flags/status (various bits)
- CRC/checksum

Manchester encoding: Each data bit encoded as two physical bits (10=0, 01=1)
"""

import struct
import logging
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TPMSReading:
    """Decoded TPMS sensor reading"""
    sensor_id: str
    pressure_kpa: Optional[float] = None
    pressure_psi: Optional[float] = None
    temperature_c: Optional[float] = None
    battery_low: Optional[bool] = None
    signal_strength: Optional[int] = None  # RSSI
    link_quality: Optional[int] = None  # LQI
    protocol: str = "Unknown"
    raw_hex: str = ""
    timestamp: str = ""
    supplier: Optional[str] = None  # e.g., "Schrader", "Siemens", "Continental"
    transmission_type: Optional[str] = None  # e.g., "Periodic", "Event-driven"
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Auto-convert between kPa and PSI
        if self.pressure_kpa and not self.pressure_psi:
            self.pressure_psi = self.pressure_kpa * 0.145038
        elif self.pressure_psi and not self.pressure_kpa:
            self.pressure_kpa = self.pressure_psi / 0.145038
    
    def get_pressure_status(self) -> str:
        """Get pressure status indicator"""
        if not self.pressure_psi:
            return "UNKNOWN"
        if self.pressure_psi < 26:
            return "CRITICAL"
        elif self.pressure_psi < 28:
            return "LOW"
        elif self.pressure_psi > 44:
            return "HIGH"
        else:
            return "NORMAL"
    
    def get_pressure_color(self) -> str:
        """Get color code for pressure status"""
        status = self.get_pressure_status()
        color_map = {
            "CRITICAL": "#ff0000",  # Red
            "LOW": "#ff9900",       # Orange
            "NORMAL": "#00ff00",    # Green
            "HIGH": "#ffff00",      # Yellow
            "UNKNOWN": "#666666"    # Gray
        }
        return color_map.get(status, "#666666")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/display"""
        return {
            'timestamp': self.timestamp,
            'sensor_id': self.sensor_id,
            'pressure_kpa': round(self.pressure_kpa, 2) if self.pressure_kpa else None,
            'pressure_psi': round(self.pressure_psi, 2) if self.pressure_psi else None,
            'temperature_c': round(self.temperature_c, 1) if self.temperature_c else None,
            'battery_low': self.battery_low,
            'rssi': self.signal_strength,
            'lqi': self.link_quality,
            'protocol': self.protocol,
            'supplier': self.supplier,
            'pressure_status': self.get_pressure_status(),
            'raw_hex': self.raw_hex
        }


class TPMSDecoder:
    """TPMS protocol decoder supporting multiple manufacturers"""
    
    # Common TPMS sync words/preambles
    SCHRADER_SYNC = [0x55, 0x55]  # Common preamble
    SIEMENS_SYNC = [0xAA, 0xAA]
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
    
    def decode_packet(self, raw_bytes: bytes, rssi: int = 0, lqi: int = 0) -> Optional[TPMSReading]:
        """
        Attempt to decode TPMS packet from raw bytes
        
        Args:
            raw_bytes: Raw packet data from CC1101
            rssi: Signal strength indicator
            lqi: Link quality indicator
            
        Returns:
            TPMSReading if decoded successfully, None otherwise
        """
        if len(raw_bytes) < 6:
            self.logger.debug(f"Packet too short: {len(raw_bytes)} bytes")
            return None
        
        raw_hex = raw_bytes.hex().upper()
        self.logger.debug(f"Decoding packet: {raw_hex}")
        
        # Try different protocol decoders
        decoders = [
            self._decode_schrader,
            self._decode_siemens,
            self._decode_generic_manchester
        ]
        
        for decoder in decoders:
            try:
                result = decoder(raw_bytes)
                if result:
                    result.signal_strength = rssi
                    result.link_quality = lqi
                    result.raw_hex = raw_hex
                    return result
            except Exception as e:
                self.logger.debug(f"Decoder {decoder.__name__} failed: {e}")
                continue
        
        # If no decoder worked, return generic info
        return self._decode_generic(raw_bytes, rssi, lqi, raw_hex)
    
    def _decode_schrader(self, data: bytes) -> Optional[TPMSReading]:
        """
        Decode Schrader TPMS protocol (common in US/European vehicles)
        
        Typical format (after Manchester decode):
        Bytes 0-3: Sensor ID (32-bit)
        Byte 4: Status/flags
        Byte 5: Pressure high byte
        Byte 6: Pressure low byte (kPa * 4)
        Byte 7: Temperature (°C + 40)
        Byte 8: CRC/checksum
        """
        # Check for Schrader sync pattern
        if len(data) < 9:
            return None
        
        # Manchester decode if needed (simplified - assumes pre-decoded)
        decoded = self._manchester_decode(data)
        if not decoded or len(decoded) < 8:
            return None
        
        # Extract fields
        sensor_id = struct.unpack('>I', decoded[0:4])[0]  # Big-endian 32-bit ID
        status = decoded[4]
        pressure_raw = struct.unpack('>H', decoded[5:7])[0]  # Big-endian 16-bit
        temp_raw = decoded[7]
        
        # Convert pressure (typically kPa * 4)
        pressure_kpa = pressure_raw / 4.0
        
        # Convert temperature (typically °C + 40)
        temperature_c = temp_raw - 40.0
        
        # Battery status (bit 7 of status byte)
        battery_low = bool(status & 0x80)
        
        # Sanity check ranges
        if not (50 < pressure_kpa < 500):  # ~7-72 PSI
            return None
        if not (-40 < temperature_c < 125):
            return None
        
        return TPMSReading(
            sensor_id=f"{sensor_id:08X}",
            pressure_kpa=pressure_kpa,
            temperature_c=temperature_c,
            battery_low=battery_low,
            protocol="Schrader",
            supplier="Schrader Electronics",
            transmission_type="Periodic (60s) + Event-driven"
        )
    
    def _decode_siemens(self, data: bytes) -> Optional[TPMSReading]:
        """
        Decode Siemens/VDO/Continental TPMS protocol
        
        Typical format:
        Bytes 0-3: Sensor ID
        Byte 4-5: Pressure (different encoding than Schrader)
        Byte 6: Temperature
        Byte 7: Status/battery
        Byte 8: CRC
        """
        decoded = self._manchester_decode(data)
        if not decoded or len(decoded) < 8:
            return None
        
        sensor_id = struct.unpack('>I', decoded[0:4])[0]
        
        # Siemens uses different pressure encoding (kPa - 100)
        pressure_raw = struct.unpack('>H', decoded[4:6])[0]
        pressure_kpa = (pressure_raw / 100.0) + 100.0
        
        # Temperature (°C + 50)
        temp_raw = decoded[6]
        temperature_c = temp_raw - 50.0
        
        status = decoded[7]
        battery_low = bool(status & 0x01)
        
        # Sanity checks
        if not (50 < pressure_kpa < 500):
            return None
        if not (-40 < temperature_c < 125):
            return None
        
        return TPMSReading(
            sensor_id=f"{sensor_id:08X}",
            pressure_kpa=pressure_kpa,
            temperature_c=temperature_c,
            battery_low=battery_low,
            protocol="Siemens/VDO",
            supplier="Siemens/Continental",
            transmission_type="Periodic (60s) + Event-driven"
        )
    
    def _decode_generic_manchester(self, data: bytes) -> Optional[TPMSReading]:
        """
        Generic Manchester decoder for unknown TPMS protocols
        Attempts to extract sensor ID and basic data
        """
        decoded = self._manchester_decode(data)
        if not decoded or len(decoded) < 6:
            return None
        
        # Assume first 4 bytes are sensor ID
        sensor_id = struct.unpack('>I', decoded[0:4])[0]
        
        # Try to guess pressure and temp from remaining bytes
        if len(decoded) >= 7:
            # Assume byte 4-5 might be pressure
            pressure_raw = decoded[4] if len(decoded) > 4 else 0
            temp_raw = decoded[5] if len(decoded) > 5 else 0
            
            # Try common encodings
            pressure_kpa = pressure_raw * 1.37  # Common multiplier
            temperature_c = temp_raw - 40.0
            
            if 50 < pressure_kpa < 500 and -40 < temperature_c < 125:
                return TPMSReading(
                    sensor_id=f"{sensor_id:08X}",
                    pressure_kpa=pressure_kpa,
                    temperature_c=temperature_c,
                    protocol="Generic-Manchester"
                )
        
        return None
    
    def _decode_generic(self, data: bytes, rssi: int, lqi: int, raw_hex: str) -> TPMSReading:
        """
        Fallback generic decoder when protocol unknown
        At minimum returns sensor ID from first 4 bytes
        """
        sensor_id = "UNKNOWN"
        if len(data) >= 4:
            sensor_id = data[0:4].hex().upper()
        
        return TPMSReading(
            sensor_id=sensor_id,
            signal_strength=rssi,
            link_quality=lqi,
            protocol="Unknown",
            raw_hex=raw_hex
        )
    
    def _manchester_decode(self, data: bytes) -> Optional[bytes]:
        """
        Manchester decoder (bit-level)
        
        Manchester encoding: each bit becomes 2 physical bits
        - 0 encoded as 10 (high-to-low transition)
        - 1 encoded as 01 (low-to-high transition)
        
        Note: Some TPMS use inverted Manchester or differential Manchester
        """
        if len(data) < 2:
            return None
        
        # For now, return simplified byte-level decode
        # TODO: Implement proper bit-level Manchester decoding with sync detection
        
        # Simple approach: assume data is already decoded or use every other bit
        result = bytearray()
        
        # Try bit-level decode
        bit_string = ''.join(format(byte, '08b') for byte in data)
        
        # Look for Manchester pairs (01 or 10)
        i = 0
        decoded_bits = []
        while i < len(bit_string) - 1:
            pair = bit_string[i:i+2]
            if pair == '10':
                decoded_bits.append('0')
                i += 2
            elif pair == '01':
                decoded_bits.append('1')
                i += 2
            else:
                # Invalid Manchester encoding, skip this bit
                i += 1
        
        # Convert decoded bits back to bytes
        if len(decoded_bits) >= 8:
            for i in range(0, len(decoded_bits) - 7, 8):
                byte_bits = ''.join(decoded_bits[i:i+8])
                result.append(int(byte_bits, 2))
        
        if len(result) >= 4:
            return bytes(result)
        
        # Fallback: return original data (may already be decoded)
        return data


def parse_csv_log(log_file: str) -> List[TPMSReading]:
    """
    Parse TPMS data from rx_profile_demo CSV log file
    
    CSV format: timestamp,mode,raw_len,raw_hex,decoded,fields
    """
    decoder = TPMSDecoder()
    readings = []
    
    try:
        with open(log_file, 'r') as f:
            # Skip header
            next(f)
            
            for line in f:
                parts = line.strip().split(',')
                if len(parts) < 4:
                    continue
                
                timestamp, mode, raw_len, raw_hex = parts[0:4]
                
                # Convert hex string to bytes
                try:
                    raw_bytes = bytes.fromhex(raw_hex)
                except ValueError:
                    continue
                
                # Decode packet
                reading = decoder.decode_packet(raw_bytes)
                if reading:
                    reading.timestamp = timestamp
                    readings.append(reading)
    
    except Exception as e:
        logger.error(f"Failed to parse log file: {e}")
    
    return readings


if __name__ == '__main__':
    # Test decoder with sample data
    logging.basicConfig(level=logging.DEBUG)
    
    # Sample Schrader TPMS packet (simulated)
    test_packet = bytes([
        0x12, 0x34, 0x56, 0x78,  # Sensor ID
        0x00,                      # Status
        0x03, 0x20,                # Pressure (800 / 4 = 200 kPa)
        0x50,                      # Temperature (80 - 40 = 40°C)
        0xAB                       # CRC
    ])
    
    decoder = TPMSDecoder()
    result = decoder.decode_packet(test_packet, rssi=-60, lqi=100)
    
    if result:
        print("✓ Decoded TPMS packet:")
        print(f"  Sensor ID: {result.sensor_id}")
        print(f"  Pressure: {result.pressure_kpa:.1f} kPa ({result.pressure_psi:.1f} PSI)")
        print(f"  Temperature: {result.temperature_c:.1f}°C")
        print(f"  Battery: {'LOW' if result.battery_low else 'OK'}")
        print(f"  Protocol: {result.protocol}")
        print(f"  RSSI: {result.signal_strength} dBm")
    else:
        print("✗ Failed to decode packet")
