#!/usr/bin/env python3
"""
PWM Speaker Module for Raspberry Pi
Uses GPIO pin 12 (physical pin 32) with hardware PWM for beep alerts.

Beep patterns:
- Single beep: General alert
- Double beep: Warning condition
- Triple beep: Critical condition
- Long beep: System event (startup, shutdown, reboot)

Supports dry-run mode for development without hardware by setting the
environment variable SPEAKER_DRY_RUN=1.
"""

import os
import time
import logging
from typing import Optional
from threading import Thread, Lock

logger = logging.getLogger(__name__)

DRY_RUN = os.getenv("SPEAKER_DRY_RUN", "0") == "1"

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available. Speaker will use dry-run if enabled.")


class Speaker:
    """PWM Speaker interface for Raspberry Pi GPIO pin 12."""

    # GPIO pin 12 (physical pin 32) - Hardware PWM channel 0
    SPEAKER_PIN = 12
    DEFAULT_FREQUENCY = 2000  # 2 kHz - pleasant beep tone
    DEFAULT_DUTY_CYCLE = 50   # 50% duty cycle for square wave

    def __init__(self, pin: int = SPEAKER_PIN):
        """
        Initialize PWM speaker on specified GPIO pin.

        Args:
            pin: GPIO pin number (BCM numbering, default: 12 for physical pin 32)
        """
        self.pin = pin
        self.pwm = None
        self.available = False
        self.beeping = False
        self.lock = Lock()

        if DRY_RUN:
            logger.info("Speaker dry-run mode enabled (no hardware required)")
            self.available = True
            return

        if not GPIO_AVAILABLE:
            logger.error("RPi.GPIO library not installed")
            return

        try:
            # Set GPIO mode to BCM numbering
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Set up pin as output
            GPIO.setup(self.pin, GPIO.OUT)
            
            # Initialize PWM on pin with default frequency
            self.pwm = GPIO.PWM(self.pin, self.DEFAULT_FREQUENCY)
            self.pwm.start(0)  # Start with 0% duty cycle (silent)
            
            self.available = True
            logger.info(f"Speaker initialized on GPIO pin {self.pin} (hardware PWM)")
        except Exception as e:
            logger.error(f"Failed to initialize speaker: {e}")
            self.available = False

    def beep(self, duration: float = 0.2, frequency: int = DEFAULT_FREQUENCY, 
             duty_cycle: int = DEFAULT_DUTY_CYCLE):
        """
        Play a single beep tone.

        Args:
            duration: Beep duration in seconds (default: 0.2)
            frequency: Beep frequency in Hz (default: 2000)
            duty_cycle: PWM duty cycle 0-100 (default: 50)
        """
        if not self.available:
            return

        with self.lock:
            if self.beeping:
                return  # Already beeping, skip

            self.beeping = True
            try:
                if DRY_RUN:
                    logger.info(f"[DRY-RUN] Beep: {duration}s @ {frequency}Hz")
                    time.sleep(duration)
                else:
                    self.pwm.ChangeFrequency(frequency)
                    self.pwm.ChangeDutyCycle(duty_cycle)
                    time.sleep(duration)
                    self.pwm.ChangeDutyCycle(0)  # Silence
            finally:
                self.beeping = False

    def beep_pattern(self, pattern: str, blocking: bool = False):
        """
        Play a beep pattern.

        Args:
            pattern: Pattern name - 'single', 'double', 'triple', 'long', 'test'
            blocking: If True, wait for pattern to complete. If False, run in background thread.
        """
        if blocking:
            self._execute_pattern(pattern)
        else:
            Thread(target=self._execute_pattern, args=(pattern,), daemon=True).start()

    def _execute_pattern(self, pattern: str):
        """Execute beep pattern (internal method)."""
        patterns = {
            'single': [(0.2, 0)],
            'double': [(0.2, 0.1), (0.2, 0)],
            'triple': [(0.2, 0.1), (0.2, 0.1), (0.2, 0)],
            'long': [(0.8, 0)],
            'test': [(0.15, 0.1), (0.15, 0.1), (0.15, 0.3), (0.3, 0)],
        }

        if pattern not in patterns:
            logger.warning(f"Unknown beep pattern: {pattern}")
            return

        for duration, pause in patterns[pattern]:
            self.beep(duration)
            if pause > 0:
                time.sleep(pause)

    def beep_gas_alert(self):
        """Beep pattern for volatile gas detection (double beep)."""
        self.beep_pattern('double', blocking=False)

    def beep_temp_alert(self):
        """Beep pattern for temperature alert (triple beep)."""
        self.beep_pattern('triple', blocking=False)

    def beep_humidity_alert(self):
        """Beep pattern for humidity alert (double beep)."""
        self.beep_pattern('double', blocking=False)

    def beep_startup(self):
        """Beep pattern for system startup (long beep)."""
        self.beep_pattern('long', blocking=True)

    def beep_shutdown(self):
        """Beep pattern for system shutdown (long beep)."""
        self.beep_pattern('long', blocking=True)

    def beep_reboot(self):
        """Beep pattern for system reboot (triple beep)."""
        self.beep_pattern('triple', blocking=True)

    def test_beep(self):
        """Play test beep pattern."""
        self.beep_pattern('test', blocking=True)

    def cleanup(self):
        """Clean up GPIO resources."""
        if self.pwm and not DRY_RUN:
            try:
                self.pwm.stop()
                GPIO.cleanup(self.pin)
                logger.info("Speaker cleanup completed")
            except Exception as e:
                logger.error(f"Error during speaker cleanup: {e}")

    def __del__(self):
        """Destructor - clean up on deletion."""
        self.cleanup()


# Global speaker instance for easy access
_speaker_instance = None

def get_speaker() -> Speaker:
    """Get global speaker instance (singleton pattern)."""
    global _speaker_instance
    if _speaker_instance is None:
        _speaker_instance = Speaker()
    return _speaker_instance


def test_speaker():
    """Test speaker functionality (for debugging)."""
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    speaker = Speaker()
    if not speaker.available:
        print("ERROR: Speaker not available")
        if not GPIO_AVAILABLE:
            print("Install with: pip install RPi.GPIO")
        print("Ensure GPIO pin 12 is available and properly wired")
        sys.exit(1)

    print("Testing speaker patterns...")
    print("Single beep...")
    speaker.beep_pattern('single', blocking=True)
    time.sleep(0.5)

    print("Double beep...")
    speaker.beep_pattern('double', blocking=True)
    time.sleep(0.5)

    print("Triple beep...")
    speaker.beep_pattern('triple', blocking=True)
    time.sleep(0.5)

    print("Long beep...")
    speaker.beep_pattern('long', blocking=True)
    time.sleep(0.5)

    print("Test pattern...")
    speaker.test_beep()

    print("Speaker test completed!")
    speaker.cleanup()


if __name__ == "__main__":
    test_speaker()
