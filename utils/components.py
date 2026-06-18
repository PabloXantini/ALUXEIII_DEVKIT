from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from utils.resources.model import (
    Model,
    CameraNode,
    MotorConfigNode,
    MotorNode,
    UltrasonicNode,
    CompassNode,
    ModelVisitor
)
from utils.pid import PIDController

class Speed(Enum):
    HIGH = 95
    MID_HIGH = 75
    MEDIUM = 60
    MID_LOW = 50
    LOW = 40
    STOP = 0
    DEFAULT = 95

class Serializer(ModelVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.cameras:list[CameraNode] = []
        self.motors:list[MotorConfigNode] = []
        self.ultrasonics:list[UltrasonicNode] = []
        self.compasses:list[CompassNode] = []

    def _visit_model(self, node:Model) -> None:
        for comp in node.l_components:
            comp.accept(self)

    def _visit_camera(self, node:CameraNode) -> None:
        self.cameras.append(node)

    def _visit_motor_config(self, node: MotorConfigNode) -> None:
        self.motors.append(node)

    def _visit_motor(self, node: MotorNode) -> None:
        pass

    def _visit_ultrasonic(self, node: UltrasonicNode) -> None:
        self.ultrasonics.append(node)

    def _visit_compass(self, node: CompassNode) -> None:
        self.compasses.append(node)

class ComponentFactory(ABC):
    def __init__(self, model_node: Model) -> None:
        self.model_node = model_node
        self.serializer = Serializer()
        self.model_node.accept(self.serializer)
    def advance(self, l:list) -> MotorConfigNode | None:
        if len(l) > 0: return l.pop(0)
        return None
    @abstractmethod
    def create_motor_controller(self)-> IMotorController:
        pass
    @abstractmethod
    def create_ultrasonic_sensor(self)-> IUltrasonicSensor:
        pass
    @abstractmethod
    def create_compass(self)-> ICompass:
        pass

class ICamera(ABC):
    def __init__(self, width:int, height:int):
        self.width = width,
        self.height = height
    
class IMotor(ABC):
    def __init__(self) -> None:
        pass
    
    def norm_vel(self, vel=Speed.DEFAULT.value, maxv=90.0):
        minv = -maxv
        clipped = max(minv, min(maxv, vel))
        norm = (maxv + clipped) / (2 * maxv)
        return minv + norm * (maxv - minv)

    @abstractmethod
    def run(self, vel: float) -> None:
        pass

class IMotorController(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def cleanup(self) -> None:
        pass

class OmniWheelMotorController(IMotorController):
    """Interface for omni-wheel motor controllers."""
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def go_from_angle(
        self, 
        angle: float, 
        vel: float = Speed.DEFAULT.value, 
        w: float = 0.0,
        calib: str = "default"
    ) -> None:
        """Move in an arbitrary direction given a heading angle in degrees (0=forward, 90=right)."""
        pass

    @abstractmethod
    def go_forward(self, vel: float = Speed.DEFAULT.value) -> None:
        pass

    @abstractmethod
    def go_backward(self, vel: float = Speed.DEFAULT.value) -> None:
        pass

    @abstractmethod
    def go_right(self, vel: float = Speed.DEFAULT.value) -> None:
        pass

    @abstractmethod
    def go_left(self, vel: float = Speed.DEFAULT.value) -> None:
        pass

    @abstractmethod
    def spin_right(self, vel: float = Speed.DEFAULT.value) -> None:
        pass

    @abstractmethod
    def spin_left(self, vel: float = Speed.DEFAULT.value) -> None:
        pass


class ICompass(ABC):
    """Abstract interface for compass sensors."""

    @abstractmethod
    def get_heading(self) -> float:
        pass


class IUltrasonicSensor(ABC):
    """Abstract interface for ultrasonic distance sensors."""

    @abstractmethod
    def get_distance(self) -> float:
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass
