import math
from abc import abstractmethod
from utils.actuators import IMotorController

class SimMotorController(IMotorController):

    # Escala para convertir las constantes de motor (ej: 80) a velocidad de simulador (ej: 4.0)
    SIM_SCALE = 0.05
    # Escala extra para la rotación (para mantener la consistencia con el divisor /40 previo)
    # SIM_TURN_SCALE = 0.05 / 40.0

    def __init__(self):
        super().__init__()
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = 0.0

    def norm_vel(self, vel, max_val, min_val=0):
        v_base = super().norm_vel(vel, max_val, min_val)
        return v_base * self.SIM_SCALE

    def reset_speeds(self):
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = 0.0

    def go_from_angle(self, angle: float, vel=None):
        """Move in an arbitrary direction; simulation decomposes angle into vx/vy components."""
        v = self.norm_vel(vel, self.HIGH)
        rad = math.radians(angle)
        self.reset_speeds()
        self.v_x = v * math.cos(rad)
        self.v_y = v * math.sin(rad)

    def go_forward(self, vel=None):
        v = self.norm_vel(vel, self.HIGH)
        self.reset_speeds()
        self.v_x = v

    def go_backward(self, vel=None):
        v = self.norm_vel(vel, self.HIGH)
        self.reset_speeds()
        self.v_x = -v

    def spin_right(self, vel=None):
        v = self.norm_vel(vel, self.MEDIUM)
        self.reset_speeds()
        self.v_turn = - v / 40

    def spin_left(self, vel=None):
        v = self.norm_vel(vel, self.MEDIUM)
        self.reset_speeds()
        self.v_turn = v / 40

    def spin_slow_right(self):
        self.spin_right(self.MID_LOW)

    def spin_slow_left(self):
        self.spin_left(self.MID_LOW)

    def stop(self):
        self.reset_speeds()
    