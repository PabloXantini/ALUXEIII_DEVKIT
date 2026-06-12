from __future__ import annotations

from robot.aluxe3.manifest import ROBOT_MODEL
from utils.config_loader import ROBOT_CONFIG, ConfigError
from .compass import Compass
from .ultrasonic import UltrasonicSensor

# Motor class is driven by the active config file
_motor_config: str = ROBOT_CONFIG.get("motor_config", "")
if _motor_config == "3W":
    from .motors3 import MotorController3W as Motors
elif _motor_config == "4W":
    from .motors4 import MotorController4W as Motors
else:
    raise ConfigError(
        f"[{ROBOT_MODEL}] Unknown motor_config value '{_motor_config}'. "
        "Expected '3W' or '4W'."
    )


class ActuatorController:
    """
    Facade actuator controller. Motor class and sensor pins are determined
    by the active robot config file declared in robot/aluxe3/manifest.py.
    """

    def __init__(self, motors: Motors = None, psensor: Compass = None, calib=None):
        us_cfg      = ROBOT_CONFIG["ultrasonic"]
        compass_cfg = ROBOT_CONFIG["compass"]
        
        if motors is None: self.motors:Motors = Motors(pins=ROBOT_CONFIG.get("motors"), calib=calib)
        else: self.motors:Motors = motors
        if psensor is None: self.psensor:Compass = Compass(bus_id=compass_cfg["bus_id"])
        else: self.psensor:Compass = psensor

        self.us_back  = UltrasonicSensor(**us_cfg["back"])
        self.us_left  = UltrasonicSensor(**us_cfg["left"])
        self.us_right = UltrasonicSensor(**us_cfg["right"])

    def get_orientation(self) -> float:
        """Returns the current absolute heading of the robot."""
        return self.psensor.get_heading()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()
        if self.us_back: self.us_back.cleanup()
        if self.us_left: self.us_left.cleanup()
        if self.us_right: self.us_right.cleanup()