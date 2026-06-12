from sandbox.sim_actuators.motors import SimMotorController

class SimMotorController4W(SimMotorController):
    """Implementación falsa del controlador de 4 motores omnidireccionales para el simulador."""

    def __init__(self):
        super().__init__()

    def go_right(self, vel=None):
        v = self.norm_vel(vel, self.MEDIUM)
        self.reset_speeds()
        self.v_y = v

    def go_left(self, vel=None):
        v = self.norm_vel(vel, self.MEDIUM)
        self.reset_speeds()
        self.v_y = -v

    def cleanup(self):
        self.stop()
