from __future__ import annotations

from .compass import SimCompass
from .ultrasonic import SimUltrasonicSensor
from utils.resources.model import ModelNode
from utils.actuators import (
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