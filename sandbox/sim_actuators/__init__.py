from __future__ import annotations

from .compass import SimCompass
from .ultrasonic import SimUltrasonicSensor
from utils.resources.model import ModelNode
from utils.actuators import (
    IActuatorController,
    ActuatorFactory, 
    IMotorController,
    IUltrasonicSensor,
    ICompass
)

class SimActuatorFactory(ActuatorFactory):
    def __init__(self, model_node:ModelNode) -> None:
        super().__init__(model_node)
    def create_motor_controller(self)-> IMotorController:
        motor_config_node = self.advance(self.serializer.motors)
        if len(motor_config_node.motors) == 3:
            from .motors3 import SimMotorController3W
            return SimMotorController3W()
        elif len(motor_config_node.motors) == 4:
            from .motors4 import SimMotorController4W
            return SimMotorController4W()
    def create_ultrasonic_sensor(self)-> IUltrasonicSensor:
        return SimUltrasonicSensor()
    def create_compass(self)-> ICompass:
        return SimCompass()

class SimActuatorController(IActuatorController):
    """
    Simulated facade controller that unifies MockMotorController and MockCompass.
    The active motor class is determined by robot/aluxe3/manifest.py.
    """

    def __init__(self, model:ModelNode):
        super().__init__(model)
        factory = SimActuatorFactory(model)
        self.motors = factory.create_motor_controller()
        self.psensor = factory.create_compass()
        self.us_back = factory.create_ultrasonic_sensor()
        self.us_left = factory.create_ultrasonic_sensor()
        self.us_right = factory.create_ultrasonic_sensor()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()
        self.us_back.cleanup()
        self.us_left.cleanup()
        self.us_right.cleanup()

# Abstract name matching the real actuator package structure.
ActuatorController = SimActuatorController
