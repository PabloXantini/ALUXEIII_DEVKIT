from __future__ import annotations

from utils.config_loader import ROBOT_CONFIG
from .compass import MockCompass, Compass
from .ultrasonic import MockUltrasonicSensor

_motor_config: str = ROBOT_CONFIG.get("motor_config", "")
if _motor_config == "3W":
    from .motors3 import MockMotorController3W as MockMotors
else:
    from .motors4 import MockMotorController4W as MockMotors


class MockActuatorController:
    """
    Simulated facade controller that unifies MockMotorController and MockCompass.
    The active motor class is determined by robot/aluxe3/manifest.py.
    """

    def __init__(self, motors: MockMotors = None, psensor: MockCompass = None, calib=None):
        us_cfg = ROBOT_CONFIG["ultrasonic"]
        self.motors: MockMotors = motors if motors is not None else MockMotors(calib=calib)
        self.psensor: MockCompass = psensor if psensor is not None else Compass(bus_id=ROBOT_CONFIG["compass"]["bus_id"])

        self.us_back  = MockUltrasonicSensor(**us_cfg["back"])
        self.us_left  = MockUltrasonicSensor(**us_cfg["left"])
        self.us_right = MockUltrasonicSensor(**us_cfg["right"])

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
ActuatorController = MockActuatorController
