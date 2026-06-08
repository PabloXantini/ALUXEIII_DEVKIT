from abc import ABC, abstractmethod

class IMotorController(ABC):
    """Abstract interface for motor controllers."""
    
    HIGH      = 80
    MID_HIGH  = 60
    MEDIUM    = 40
    MID_LOW   = 30
    LOW       = 20

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def go_from_angle(self, angle: float, vel: float = None) -> None:
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
    def spin_slow_right(self) -> None:
        pass

    @abstractmethod
    def spin_slow_left(self) -> None:
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
