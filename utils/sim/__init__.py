from __future__ import annotations

from .compass import SimCompass
from .ultrasonic import SimUltrasonicSensor
from utils.resources.model import Model
from utils.components import (
    ComponentFactory,
    ICamera, 
    IMotorController,
    IUltrasonicSensor,
    ICompass
)
from utils.sim.virtual_camera import VirtualCamera

class SimComponentFactory(ComponentFactory):
    def __init__(self, model_node:Model) -> None:
        super().__init__(model_node)
    def create_camera(self) -> ICamera:
        camera_node = self.advance(self.serializer.cameras)
        p = camera_node.properties
        return VirtualCamera(
            width=p.get('width', 640), 
            height=p.get('height', 480), 
            scale=p.get('scale', 100.0),
            fov_degrees=p.get('fov', 45),
            pitch=p.get('pitch', 30.0),
            camera_height=p.get('h', 30.0)
        )
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