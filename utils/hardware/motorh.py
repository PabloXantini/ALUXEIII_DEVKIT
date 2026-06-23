from __future__ import annotations

try:
    import RPi.GPIO as GPIO
except ImportError:
    from utils.mock import MockGPIO
    GPIO = MockGPIO()
    
from utils.resources.model import MotorNode
from utils.components import OmniWheelMotorController, IMotor, Speed
from utils.resources.config import (
    ConfigVisitor,
    ConfigError,
    ConfigMissingAttribute
)
import utils.gpio as gpio

class MotorHValidator(ConfigVisitor):
    def __init__(self) -> None:
        super().__init__()
    def _visit_motor(self, node:MotorNode) -> None:
        labels = node.properties.keys()
        if ("in1" not in labels or 
            "in2" not in labels or 
            "en" not in labels):
            raise ConfigMissingAttribute(
                f"[Model ({node.model}): {node.label}] Missing required attributes in motor config"
            )

class MotorH(IMotor):
    """
    Class that resumes the bridge H motor driven control
    """
    def __init__(self, motor:MotorNode):
        super().__init__()
        validator = MotorHValidator()
        motor.accept(validator)
        self._p = motor.properties
        self.in1 = self._p["in1"]
        self.in2 = self._p["in2"]
        self.en = self._p["en"]
        gpio.init()
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.en, GPIO.OUT)
        self.pwm = GPIO.PWM(self.en, 1000)
        self.pwm.start(0)        

    def _fwd(self, in1, in2, pwm, vel):
        """Drive motor forward."""
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        pwm.ChangeDutyCycle(vel)

    def _bwd(self, in1, in2, pwm, vel):
        """Drive motor backward."""
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        pwm.ChangeDutyCycle(vel)

    def stop(self):
        """Stop the motor."""
        self.last_vel = 0.0
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)
    
    def run(self, speed: float, calib:float = 1.0) -> None:
        """Set the motor speed."""
        v = self.norm_vel(speed * calib)
        self.last_vel = v
        if v >= 0:
            self._fwd(self.in1, self.in2, self.pwm, v)
        else:
            self._bwd(self.in1, self.in2, self.pwm, abs(v))
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        self.pwm.stop()

class OmniMotorHController(OmniWheelMotorController):
    def __init__(self, config:list[MotorNode], calib:dict = {}) -> None:
        super().__init__()
        if config is None:
            raise ConfigError("Motor configuration must be specified.")
        self.calib = calib

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        GPIO.cleanup()
