from abc import ABC, abstractmethod

class IMotorController(ABC):
    """Abstract interface for motor controllers."""
    
    HIGH      = 95
    MID_HIGH  = 75
    MEDIUM    = 60
    MID_LOW   = 50
    LOW       = 40

    def _norm_vel(self, vel, max_val, min_val=0.0):
        if vel is None:
            return max_val
        norm = max(0.0, min(100.0, float(vel))) / 100.0
        return min_val + norm * (max_val - min_val)

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
