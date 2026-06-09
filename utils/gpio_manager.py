from __future__ import annotations

try:
    import RPi.GPIO as GPIO
except ImportError:
    from utils.mock import MockGPIO
    GPIO = MockGPIO()


def init_gpio(mode=GPIO.BCM) -> None:
    """
    Initialize GPIO pin numbering mode exactly once.
    Safe to call from multiple actuator constructors.
    """
    current = GPIO.getmode()
    if current is None:
        GPIO.setwarnings(False)
        GPIO.setmode(mode)
