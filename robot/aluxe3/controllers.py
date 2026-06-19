from robot.aluxe3.context import Aluxe3Context
from utils.components import ComponentFactory
from utils.resources.config import ConfigError
from utils.resources.model import Model
from utils.pid import PIDController

class ActuatorController:
    """Abstract interface for actuator controllers."""
    def __init__(self, model:Model) -> None:
        if model is None:
            raise ConfigError("No model configuration found in the model config.")
    def _init_components(self, factory:ComponentFactory) -> None:
        self.motors = factory.create_motor_controller()
        self.us_left = factory.create_ultrasonic_sensor()
        self.us_right = factory.create_ultrasonic_sensor()
        self.us_back = factory.create_ultrasonic_sensor()
        self.psensor = factory.create_compass()
    def cleanup(self) -> None:
        """Clean up resources for all child components."""
        self.motors.cleanup()
        if self.us_left: self.us_left.cleanup()
        if self.us_right: self.us_right.cleanup()
        if self.us_back: self.us_back.cleanup()

class CameraController:
    def __init__(self, model:Model) -> None:
        if model is None:
            raise ConfigError("No source configuration found in the source config.")
    def _init_components(self, factory:ComponentFactory) -> None:
        self.front_cam = factory.create_camera()
    def cleanup(self) -> None:
        """Clean up resources for all child components."""
        self.front_cam.cleanup()

class AnglePIDController(PIDController):
    def __init__(self, src:Aluxe3Context, kp:float, ki:float, kd:float) -> None:
        super().__init__(src, Kp=kp, Ki=ki, Kd=kd)

    def capture(self, setpoint:float) -> float:
        return self.src.env.heading