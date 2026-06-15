from utils.actuators import ActuatorFactory
from utils.resources.config import ConfigError
from utils.resources.model import ModelNode

class ActuatorController:
    """Abstract interface for actuator controllers."""
    def __init__(self, model:ModelNode) -> None:
        if model is None:
            raise ConfigError("No model configuration found in the model config.")
    def _init_components(self, factory:ActuatorFactory) -> None:
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
