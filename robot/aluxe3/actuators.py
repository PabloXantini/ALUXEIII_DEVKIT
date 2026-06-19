from __future__ import annotations

from utils.resources.model import Model
from utils.hardware import HardwareFactory
from utils.sim import SimComponentFactory
from robot.aluxe3.controllers import ActuatorController, CameraController

class HardwareActuatorController(ActuatorController):
    """
    Facade actuator controller. Motor class and sensor pins are determined
    by the active robot config file loaded via utils.resources.model.
    """
    def __init__(self, model:Model):
        super().__init__(model)
        factory = HardwareFactory(model)
        self._init_components(factory)

class HardwareCameraController(CameraController):
    def __init__(self, model:Model):
        super().__init__(model)
        factory = HardwareFactory(model)
        self._init_components(factory)

class SimActuatorController(ActuatorController):
    """
    Simulated facade controller that unifies MockMotorController and MockCompass.
    The active motor class is determined by robot/aluxe3/manifest.py.
    """
    def __init__(self, model:Model):
        super().__init__(model)
        factory = SimComponentFactory(model)
        self._init_components(factory)

class SimCameraController(CameraController):
    def __init__(self, model:Model):
        super().__init__(model)
        factory = SimComponentFactory(model)
        self._init_components(factory)