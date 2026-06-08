from __future__ import annotations
from .motors4 import MockMotorController4W as MockMotorController
from .motors3 import MockMotorController3W
from .compass import MockCompass, Compass
from .ultrasonic import MockUltrasonicSensor

class MockActuatorController:
    """
    Simulated facade controller that unifies MockMotorController and MockGY87Bridge.
    Provides access to self.motors and self.psensor for simulation.
    
    Author: PabloXantini (Placeholder as per guidelines)
    """

    def __init__(self, motors: MockMotorController = None, psensor: MockCompass = None, calib=None, bus_id=1):
        # Allow injection of custom or mock instances for extensibility
        self.motors: MockMotorController = motors if motors is not None else MockMotorController(calib=calib)
        self.psensor: MockCompass = psensor if psensor is not None else Compass(bus_id=bus_id)
        
        self.us_back = MockUltrasonicSensor(9, 11)
        self.us_left = MockUltrasonicSensor(4, 10)
        self.us_right = MockUltrasonicSensor(7, 8)

    def get_orientation(self) -> float:
        """Returns the current absolute heading of the robot."""
        return self.psensor.get_heading()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()
        self.us_back.cleanup()
        self.us_left.cleanup()
        self.us_right.cleanup()


# Abstract names matching the real actuator package structure
ActuatorController = MockActuatorController
MotorController = MockMotorController
