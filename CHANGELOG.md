# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
- **Deployment Script Enhancements**: Added safety confirmation prompts requiring branch name verification before deployment
- **Touch Input Fixes**: Improved touchscreen support with better coordinate mapping, enhanced logging, and more reliable button detection
- **Documentation Updates**: Comprehensive documentation improvements across all README files and deployment guides
- Rename `scripts/` to `install/` and add install wrappers for display and RF.
- Display: prefer `/boot/firmware/config.txt`, comment generic `vc4` overlays and add `dtoverlay=vc4-kms-dsi-4.3inch` idempotently.
- Add venv-based install flow and update systemd unit to use venv Python.
- Add `install/install_rf.sh`, `install/display_install.sh`, `install/install_service.sh`, `install/venv_setup.sh` helpers.

