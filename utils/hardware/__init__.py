from __future__ import annotations

from .compass import Compass
from .ultrasonic import UltrasonicSensor
from utils.resources.config import ConfigError
from utils.resources.model import Model
from utils.components import (
    ComponentFactory,
    OmniWheelMotorController,
    IUltrasonicSensor,
    ICompass
)
from robot.aluxe3.controllers import ActuatorController

class HardwareActuatorFactory(ComponentFactory):
    def __init__(self, model_node: Model):
        super().__init__(model_node)
        self.camera_pointer = 0
        self.motor_pointer = 0
        self.ultrasonic_pointer = 0
        self.compass_pointer = 0
    def create_motor_controller(self)-> OmniWheelMotorController:
        motor_config_node = self.advance(self.serializer.motors)
        if motor_config_node.type == "Omni":
            if len(motor_config_node.motors) == 3:
                from .motors3 import OmniMotorHController3W
                return OmniMotorHController3W(motor_config_node.motors, motor_config_node.calibration)
            elif len(motor_config_node.motors) == 4:
                from .motors4 import OmniMotorHController4W
                return OmniMotorHController4W(motor_config_node.motors, motor_config_node.calibration)
        else:
            raise ConfigError(f"Unsupported motor type: {motor_config_node.type}")
        
    def create_ultrasonic_sensor(self)-> IUltrasonicSensor:
        ultrasonic_node = self.advance(self.serializer.ultrasonics)
        if ultrasonic_node.type == "default":
            return UltrasonicSensor(**ultrasonic_node.properties)
        else:
            raise ConfigError(f"Unsupported ultrasonic type: {ultrasonic_node.type}")
    def create_compass(self)-> ICompass:
        compass_node = self.advance(self.serializer.compasses)
        if compass_node.type == "default":
            return Compass(**compass_node.properties)
        else:
            raise ConfigError(f"Unsupported compass type: {compass_node.type}")

class HardwareActuatorController(ActuatorController):
    """
    Facade actuator controller. Motor class and sensor pins are determined
    by the active robot config file loaded via utils.resources.model.
    """
    def __init__(self, model:Model):
        super().__init__(model)
        factory = HardwareActuatorFactory(model)
        self._init_components(factory)