from utils.sim.motors import SimMotorController
from utils.components import Speed

class SimMotorController4W(SimMotorController):
    """Implementación falsa del controlador de 4 motores omnidireccionales para el simulador."""

    def __init__(self):
        super().__init__()

    def go_right(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.reset_speeds()
        self.v_y = v

    def go_left(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.reset_speeds()
        self.v_y = -v

    def cleanup(self):
        self.stop()
