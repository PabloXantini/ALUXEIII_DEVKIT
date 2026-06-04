from __future__ import annotations
from .motors import MotorController
from .gy87 import GY87Bridge

class ActuatorController:
    """
    Facade actuator controller that holds motors and sensors (physical sensor/psensor).
    Provides access to self.motors and self.psensor for scaling components.
    
    Author: PabloXantini (Placeholder as per guidelines)
    """

    def __init__(self, motors: MotorController = None, psensor: GY87Bridge = None, calib=None, bus_id=1):
        # Allow injection of custom or mock instances for extensibility
        self.motors: MotorController = motors if motors is not None else MotorController(calib=calib)
        self.psensor: GY87Bridge = psensor if psensor is not None else GY87Bridge(bus_id=bus_id)

    def get_orientation(self) -> float:
        """Returns the current absolute heading of the robot."""
        return self.psensor.get_heading()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()