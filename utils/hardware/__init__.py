from __future__ import annotations

from .compass import Compass
from .ultrasonic import UltrasonicSensor
from utils.resources.config import ConfigError
from utils.resources.model import Model
from utils.components import (
    ComponentFactory,
    ICamera,
    IMotorController,
    IUltrasonicSensor,
    ICompass
)

class HardwareFactory(ComponentFactory):
    def __init__(self, model_node: Model):
        super().__init__(model_node)
        self.camera_pointer = 0
        self.motor_pointer = 0
        self.ultrasonic_pointer = 0
        self.compass_pointer = 0
        self.camera_pointer = 0
    def create_camera(self)-> ICamera:
        camera_node = self.advance(self.serializer.cameras)
        p = camera_node.properties
        if camera_node.type == "default":
            from .camera import Camera
            return Camera(p['src'], p['width'], p['height'], p.get('scale', 100.0))
        else:
            raise ConfigError(f"Unsupported camera type: {camera_node.type}")
    def create_motor_controller(self)-> IMotorController:
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
        p = ultrasonic_node.properties
        if ultrasonic_node.type == "default":
            return UltrasonicSensor(p['trig'], p['echo'])
        else:
            raise ConfigError(f"Unsupported ultrasonic type: {ultrasonic_node.type}")
    def create_compass(self)-> ICompass:
        compass_node = self.advance(self.serializer.compasses)
        p = compass_node.properties
        if compass_node.type == "default":
            return Compass(p['bus_id'])
        else:
            raise ConfigError(f"Unsupported compass type: {compass_node.type}")