from __future__ import annotations
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    from utils.mock import MockGPIO
    GPIO = MockGPIO()

from utils.components import IUltrasonicSensor
import utils.gpio as gpio

class UltrasonicSensor(IUltrasonicSensor):
    """
    Class encapsulating the functionality of an ultrasonic sensor.
    """
    
    def __init__(self, trig: int = 23, echo: int = 24):
        self._trig_pin = trig
        self._echo_pin = echo
        gpio.init()
        GPIO.setup(self._trig_pin, GPIO.OUT)
        GPIO.setup(self._echo_pin, GPIO.IN)

    def get_distance(self) -> float:
        """
        Calculates and returns the distance based on the speed of sound (34300 cm/s).
        Returns -1.0 if there is a timeout.
        """
        # Send a short pulse to the trigger pin
        GPIO.output(self._trig_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self._trig_pin, GPIO.LOW)

        # Measure the duration for the echo pulse
        pulse_start = time.time()
        pulse_end = time.time()
        timeout = pulse_start + 0.04 # 40ms timeout ~ 6.8m max distance
        
        while GPIO.input(self._echo_pin) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                return -1.0

        while GPIO.input(self._echo_pin) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                return -1.0

        pulse_duration = pulse_end - pulse_start

        # Calculate the distance based on the speed of sound (34300 cm/s)
        distance = pulse_duration * 34300 / 2

        return distance
        
    def cleanup(self) -> None:
        """
        Cleans up the GPIO configuration.
        """
        GPIO.cleanup()
