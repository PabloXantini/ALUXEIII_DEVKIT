from __future__ import annotations

from utils.config_loader import ROBOT_CONFIG
from .compass import SimCompass
from .ultrasonic import SimUltrasonicSensor

_motor_config: str = ROBOT_CONFIG.get("motor_config", "")
if _motor_config == "3W":
    from .motors3 import SimMotorController3W as SimMotors
else:
    from .motors4 import SimMotorController4W as SimMotors


class SimActuatorController:
    """
    Simulated facade controller that unifies MockMotorController and MockCompass.
    The active motor class is determined by robot/aluxe3/manifest.py.
    """

    def __init__(self):
        self.motors: SimMotors = SimMotors()
        self.psensor: SimCompass = SimCompass()
        self.us_back: SimUltrasonicSensor  = SimUltrasonicSensor()
        self.us_left: SimUltrasonicSensor  = SimUltrasonicSensor()
        self.us_right: SimUltrasonicSensor = SimUltrasonicSensor()

    def get_orientation(self) -> float:
        """Returns the current absolute heading of the robot."""
        return self.psensor.get_heading()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()
        self.us_back.cleanup()
        self.us_left.cleanup()
        self.us_right.cleanup()


# Abstract name matching the real actuator package structure.
ActuatorController = SimActuatorController
