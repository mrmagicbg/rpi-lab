#!/bin/bash
# Script to setup RF Lab on Raspberry Pi
# Run this on your Raspberry Pi after cloning the repo

set -euo pipefail

echo "=== RF Lab Setup Script ==="
echo ""

# Navigate to repo (assume it's in /opt/rpi-lab or ~/rpi-lab)
if [ -d "/opt/rpi-lab" ]; then
    cd /opt/rpi-lab/rf || { echo "Error: /opt/rpi-lab/rf directory not found"; exit 1; }
elif [ -d "$HOME/rpi-lab" ]; then
    cd "$HOME/rpi-lab/rf" || { echo "Error: $HOME/rpi-lab/rf directory not found"; exit 1; }
else
    echo "Error: rpi-lab directory not found in /opt or $HOME"
    exit 1
fi

# Navigate to CC1101 directory
cd CC1101 || { echo "Error: CC1101 directory not found"; exit 1; }

# Check if WiringPi is installed
if ! command -v gpio &> /dev/null; then
    echo "WiringPi not found. Installing..."
    ORIG_DIR=$(pwd)
    cd ~
    if [ "$(uname -m)" = "aarch64" ]; then
        wget -q https://github.com/WiringPi/WiringPi/releases/download/3.6/wiringpi_3.6_arm64.deb
        sudo dpkg -i wiringpi_3.6_arm64.deb
    else
        wget -q https://github.com/WiringPi/WiringPi/releases/download/3.6/wiringpi_3.6_armhf.deb
        sudo dpkg -i wiringpi_3.6_armhf.deb
    fi
    cd "$ORIG_DIR"
fi

# Build rx_profile_demo
echo ""
echo "Building rx_profile_demo..."
g++ -o rx_profile_demo rx_profile_demo.cpp cc1100_raspi.cpp cc1100_globals.cpp -lwiringPi
if [ $? -eq 0 ]; then
    chmod +x rx_profile_demo
    echo "✓ Build successful!"
else
    echo "✗ Build failed!"
    exit 1
fi

# Build RX_Demo and TX_Demo (optional)
echo ""
echo "Building RX_Demo and TX_Demo..."
if [ -f "RX_Demo.cpp" ]; then
    g++ -o RX_Demo RX_Demo.cpp cc1100_raspi.cpp cc1100_globals.cpp -lwiringPi
    chmod +x RX_Demo
    echo "✓ RX_Demo built"
fi

if [ -f "TX_Demo.cpp" ]; then
    g++ -o TX_Demo TX_Demo.cpp cc1100_raspi.cpp cc1100_globals.cpp -lwiringPi
    chmod +x TX_Demo
    echo "✓ TX_Demo built"
fi

# Show results
echo ""
echo "=== Build Complete ==="
ls -lh rx_profile_demo RX_Demo TX_Demo 2>/dev/null | grep -v "^total"

echo ""
echo "=== Quick Test ==="
echo "Running: sudo ./rx_profile_demo -h"
echo ""
sudo ./rx_profile_demo -h

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Try these commands:"
echo "  sudo ./rx_profile_demo -mTPMS    # TPMS mode (433 MHz)"
echo "  sudo ./rx_profile_demo -mIoT     # IoT mode (868 MHz)"
echo ""
echo "See SETUP_GUIDE.md for full documentation"
