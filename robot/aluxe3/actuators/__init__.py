from __future__ import annotations

from robot.aluxe3.manifest import MOTOR_CONFIG
from .compass import Compass
from .ultrasonic import UltrasonicSensor

if MOTOR_CONFIG == "3W":
    from .motors3 import MotorController3W as Motors
else:
    from .motors4 import MotorController4W as Motors


class ActuatorController:
    """
    Facade actuator controller that holds motors and sensors.
    The active motor class is determined by robot/aluxe3/manifest.py.
    """
    def __init__(self, motors: Motors = None, psensor: Compass = None, calib=None, bus_id=1):
        self.motors: Motors = motors if motors is not None else Motors(calib=calib)
        self.psensor: Compass = psensor if psensor is not None else Compass(bus_id=bus_id)
        self.us_back = UltrasonicSensor(9, 11)
        self.us_left = UltrasonicSensor(26, 21)
        self.us_right = UltrasonicSensor(8, 7)

    def get_orientation(self) -> float:
        """Returns the current absolute heading of the robot."""
        return self.psensor.get_heading()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()
        if self.us_back: self.us_back.cleanup()
        if self.us_left: self.us_left.cleanup()
        if self.us_right: self.us_right.cleanup()