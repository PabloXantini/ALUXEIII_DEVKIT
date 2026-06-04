from __future__ import annotations
from .motors import MockMotorController
from .gy87 import MockGY87Bridge, GY87Bridge

class MockActuatorController:
    """
    Simulated facade controller that unifies MockMotorController and MockGY87Bridge.
    Provides access to self.motors and self.psensor for simulation.
    
    Author: PabloXantini (Placeholder as per guidelines)
    """

    def __init__(self, motors: MockMotorController = None, psensor: MockGY87Bridge = None, calib=None, bus_id=1):
        # Allow injection of custom or mock instances for extensibility
        self.motors: MockMotorController = motors if motors is not None else MockMotorController(calib=calib)
        self.psensor: MockGY87Bridge = psensor if psensor is not None else GY87Bridge(bus_id=bus_id)

    def get_orientation(self) -> float:
        """Returns the current absolute heading of the robot."""
        return self.psensor.get_heading()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()


# Abstract names matching the real actuator package structure
ActuatorController = MockActuatorController
MotorController = MockMotorController
