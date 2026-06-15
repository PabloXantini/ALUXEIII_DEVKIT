from __future__ import annotations

from .compass import Compass
from .ultrasonic import UltrasonicSensor
from utils.resources.config import ConfigError
from utils.resources.model import ModelNode
from utils.actuators import (
    ActuatorFactory,
    IActuatorController,
    IMotorController,
    IUltrasonicSensor,
    ICompass
)

class HardwareActuatorFactory(ActuatorFactory):
    def __init__(self, model_node: ModelNode):
        super().__init__(model_node)
        self.motor_pointer = 0
        self.ultrasonic_pointer = 0
        self.compass_pointer = 0
        
    def create_motor_controller(self)-> IMotorController:
        motor_config_node = self.advance(self.serializer.motors)
        if motor_config_node.type == "Omni":
            if len(motor_config_node.motors) == 3:
                from .motors3 import MotorController3W
                return MotorController3W(motor_config_node.motors, motor_config_node.calibration)
            elif len(motor_config_node.motors) == 4:
                from .motors4 import MotorController4W
                return MotorController4W(motor_config_node.motors, motor_config_node.calibration)
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

class ActuatorController(IActuatorController):
    """
    Facade actuator controller. Motor class and sensor pins are determined
    by the active robot config file loaded via utils.resources.model.
    """

    def __init__(self, model:ModelNode):
        super().__init__(model)
        factory = HardwareActuatorFactory(model)
        self.motors = factory.create_motor_controller()
        self.us_back = factory.create_ultrasonic_sensor()
        self.us_left = factory.create_ultrasonic_sensor()
        self.us_right = factory.create_ultrasonic_sensor()
        self.psensor = factory.create_compass()

    def cleanup(self):
        """Clean up resources for all child components."""
        self.motors.cleanup()
        if self.us_back: self.us_back.cleanup()
        if self.us_left: self.us_left.cleanup()
        if self.us_right: self.us_right.cleanup()