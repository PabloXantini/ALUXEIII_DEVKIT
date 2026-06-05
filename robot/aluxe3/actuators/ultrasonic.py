from __future__ import annotations
import RPi.GPIO as GPIO
import time

from utils.actuators import IUltrasonicSensor

class UltrasonicSensor(IUltrasonicSensor):
    """
    Class encapsulating the functionality of an ultrasonic sensor.
    """
    
    def __init__(self, trig_pin: int = 23, echo_pin: int = 24):
        self._trig_pin = trig_pin
        self._echo_pin = echo_pin
        # Set the GPIO mode (BCM or BOARD)
        GPIO.setmode(GPIO.BCM)
        # Set the trigger and echo pins
        GPIO.setup(self._trig_pin, GPIO.OUT)
        GPIO.setup(self._echo_pin, GPIO.IN)

    def get_distance(self) -> float:
        """
        Calculates and returns the distance based on the speed of sound (34300 cm/s).
        """
        # Send a short pulse to the trigger pin
        GPIO.output(self._trig_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self._trig_pin, GPIO.LOW)

        # Measure the duration for the echo pulse
        pulse_start = time.time()
        pulse_end = time.time()
        
        while GPIO.input(self._echo_pin) == 0:
            pulse_start = time.time()

        while GPIO.input(self._echo_pin) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        # Calculate the distance based on the speed of sound (34300 cm/s)
        distance = pulse_duration * 34300 / 2

        return distance
        
    def cleanup(self) -> None:
        """
        Cleans up the GPIO configuration.
        """
        GPIO.cleanup()
