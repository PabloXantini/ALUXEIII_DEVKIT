from __future__ import annotations
from .motors import MotorController
from .compass import Compass
from .ultrasonic import UltrasonicSensor

class ActuatorController:
    """
    Facade actuator controller that holds motors and sensors (physical sensor/psensor).
    Provides access to self.motors and self.psensor for scaling components.
    
    Author: PabloXantini (Placeholder as per guidelines)
    """

    def __init__(self, motors: MotorController = None, psensor: Compass = None, calib=None, bus_id=1):
        # Allow injection of custom or mock instances for extensibility
        self.motors: MotorController = motors if motors is not None else MotorController(calib=calib)
        self.psensor: Compass = psensor if psensor is not None else Compass(bus_id=bus_id)
        
        self.us_back = UltrasonicSensor(9, 11)
        self.us_left = UltrasonicSensor(4, 10)
        self.us_right = UltrasonicSensor(2, 3)

    def get_orientation(self) -> float:
        """Returns the current absolute heading of the robot."""
        return self.psensor.get_heading()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()
        if self.us_back: self.us_back.cleanup()
        if self.us_left: self.us_left.cleanup()
        if self.us_right: self.us_right.cleanup()