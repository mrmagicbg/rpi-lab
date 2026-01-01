"""
RF (Radio Frequency) modules for RPI Lab.

This package provides TPMS (Tire Pressure Monitoring System) decoding and monitoring:
- TPMS protocol decoders (Schrader, Siemens/VDO, Generic Manchester)
- Data logging in CSV and JSON formats
- Real-time monitoring GUI

Supported Hardware:
- CC1101 RF transceiver module (433.92 MHz)
- Various TPMS sensor protocols

Example:
    >>> from rf.tpms_decoder import TPMSDecoder, TPMSReading
    >>> decoder = TPMSDecoder()
    >>> reading = decoder.decode_packet(raw_bytes, rssi=-60, lqi=100)
    >>> if reading:
    ...     print(f"Sensor {reading.sensor_id}: {reading.pressure_psi} PSI")
"""

__version__ = "0.5.0"
__all__ = ["TPMSDecoder", "TPMSReading", "TPMSLogger"]

from rf.tpms_decoder import TPMSDecoder, TPMSReading
from rf.tpms_logger import TPMSLogger
