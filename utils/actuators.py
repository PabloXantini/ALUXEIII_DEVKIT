from abc import ABC, abstractmethod

class IMotorController(ABC):
    """Abstract interface for motor controllers."""

    @abstractmethod
    def stop(self) -> None:
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
