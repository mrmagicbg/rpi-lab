# Changelog

All notable changes to this project are documented in this file.

For detailed version history and older releases, see [docs/CHANGELOG_ARCHIVE.md](docs/CHANGELOG_ARCHIVE.md).

## [3.0.7] - 2026-01-09

### Added - TUI Aliases & Documentation Consolidation
- Convenient bash aliases for quick TUI access via SSH
- Aliases automatically created during installation in ~/.bash_aliases
- Consolidated documentation with index in root README
- Created [docs/TUI_SETUP.md](docs/TUI_SETUP.md) with complete alias setup and troubleshooting
- Updated README.md with links to detailed docs in docs/ folder

### Docs
- Single README.md in root with documentation index
- Single CHANGELOG.md in root with recent changes
- Detailed documentation moved to docs/ folder
- TUI alias setup instructions in [docs/TUI_SETUP.md](docs/TUI_SETUP.md)

## [3.0.6] - 2026-01-08

### Changed
- Gas alert beeping now only triggers for "Gas Detected" level (< 5kΩ)
- Previous threshold of 50kΩ caused false alerts during normal warm-up
- Beeping remains at 15-second intervals when true gas detection occurs

## [3.0.5] - 2026-01-08

### Added
- TUI (Text User Interface) for SSH monitoring
- Color-coded gas heater status display (7 levels)
- Enhanced gas label with status text and resistance values

## [3.0.4] - 2026-01-08

### Added
- Real-time gas heater status display with 7 color levels
- Comprehensive deploy script help (-h/--help)

## [3.0.3] - 2026-01-08

### Fixed
- BME690 real hardware readings (removed dry-run mode)
- TPMS decoder syntax error (missing docstring quote)

## [3.0.2] - 2026-01-08

### Fixed
- Updated bme690 to 1.0.0 and smbus2 to 0.6.0

## [3.0.1] - 2026-01-08

### Fixed
- Deployment hanging at package installation
- RF compilation errors with directory navigation

---

For older releases and detailed changelog, see [docs/CHANGELOG_ARCHIVE.md](docs/CHANGELOG_ARCHIVE.md).
