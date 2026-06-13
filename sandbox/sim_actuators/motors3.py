from sandbox.sim_actuators.motors import SimMotorController

class SimMotorController3W(SimMotorController):
    """Implementación falsa del controlador de 3 motores omnidireccionales para el simulador."""

    def __init__(self):
        super().__init__()

    def go_right(self, vel=None):
        self.go_from_angle(90, vel)

    def go_left(self, vel=None):
        self.go_from_angle(270, vel)

    def cleanup(self):
        self.stop()
