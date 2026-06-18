from utils.sim.motors import SimMotorController
from utils.components import Speed

class SimMotorController3W(SimMotorController):
    """Implementación falsa del controlador de 3 motores omnidireccionales para el simulador."""

    def __init__(self):
        super().__init__()

    def go_left(self, vel=Speed.DEFAULT.value):
        self.go_from_angle(angle=90, vel=vel)

    def go_right(self, vel=Speed.DEFAULT.value):
        self.go_from_angle(angle=270, vel=vel)

    def cleanup(self):
        self.stop()
