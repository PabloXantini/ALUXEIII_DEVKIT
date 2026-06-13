from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum

class Speed(Enum):
    HIGH = 95
    MID_HIGH = 75
    MEDIUM = 60
    MID_LOW = 50
    LOW = 40
    STOP = 0

class IMotorController(ABC):
    """Abstract interface for motor controllers."""
    def __init__(self) -> None:
        pass

    def norm_vel(self, vel, minv=0.0, maxv=90.0):
        if vel is None: vel = Speed.HIGH.value
        norm = max(minv, min(maxv, float(vel))) / maxv
        return minv + norm * (maxv - minv)

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def go_from_angle(self, angle: float, vel: float = None, calib: dict | None = None) -> None:
        """Move in an arbitrary direction given a heading angle in degrees (0=forward, 90=right)."""
        pass

    @abstractmethod
    def go_forward(self, vel: float = None) -> None:
        pass

    @abstractmethod
    def go_backward(self, vel: float = None) -> None:
        pass

    @abstractmethod
    def go_right(self, vel: float = None) -> None:
        pass

    @abstractmethod
    def go_left(self, vel: float = None) -> None:
        pass

    @abstractmethod
    def spin_right(self, vel: float = None) -> None:
        pass

    @abstractmethod
    def spin_left(self, vel: float = None) -> None:
        pass

    @abstractmethod
    def cleanup(self) -> None:
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
