from abc import ABC, abstractmethod

class PIDController(ABC):
    def __init__(self, src, Kp:float, Ki:float, Kd:float) -> None:
        self.src = src
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_e = 0.0
        self.acc_e = 0.0

    @abstractmethod
    def capture(self, setpoint:float) -> float:
        """Read the measured value from the source context."""
        pass

    def calculate(self, setpoint:float) -> float:
        measured = self.capture(setpoint)
        error = setpoint - measured          # proportional
        delta = error - self.last_e          # derivative
        self.acc_e += error                  # integral accumulator
        self.last_e = error
        return self.Kp * error + self.Ki * self.acc_e + self.Kd * delta

    def reset(self) -> None:
        """Reset integrator and derivative state."""
        self.last_e = 0.0
        self.acc_e = 0.0