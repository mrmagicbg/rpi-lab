# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-11-23

### Added
- Initial release of RF Lab toolkit
- CC1101 driver for Raspberry Pi (forked from [SpaceTeddy/CC1101](https://github.com/SpaceTeddy/CC1101))
- TPMS profile (mode 0x07) for automotive tire pressure sensors
  - 433.92 MHz, 2-FSK with Manchester encoding
  - ~19.2 kbps bitrate, ±47 kHz deviation
  - Optimized for Siemens VDO and Schrader sensors
- TFA IT+ IoT profile (mode 0x08) for weather sensors
  - 868.3 MHz, ASK/OOK modulation
  - ~2.4-4.8 kbps bitrate
  - Supports TFA Dostmann IT+ protocol
- Profile demo tool (`rx_profile_demo.cpp`) with CLI argument parsing
  - `-mTPMS` and `-mIoT` mode switches
  - Frequency and channel selection
  - Debug output and register dumping
- Comprehensive README with:
  - Profile specifications and use cases
  - Hardware wiring diagrams
  - Build and usage instructions
  - Troubleshooting guide
- Project documentation:
  - CHANGELOG.md for version tracking
  - .gitignore for clean repository
  - MIT License (inherited from base library)

### Technical Details
- Extended `set_mode()` with cases 0x07 (TPMS) and 0x08 (IoT)
- Added RF specification comments in driver source
- Configuration arrays generated via SmartRF Studio
- Tested on Raspberry Pi with WiringPi SPI interface

## [Unreleased]

### Planned
- Manchester decoder implementation for TPMS data extraction
- OOK pulse-width decoder for IT+ protocol
- CRC validation routines
- Additional profiles:
  - LoRa modulation support
  - Additional TPMS variants (315 MHz)
  - Z-Wave receiver mode
- Web-based configuration interface
- Real-time signal visualization
- Packet logging and replay functionality
