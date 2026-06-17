import math
from utils.components import OmniWheelMotorController, Speed

class SimMotorController(OmniWheelMotorController):
    # Escala para convertir las constantes de motor (ej: 80) a velocidad de simulador (ej: 4.0)
    SIM_SCALE = 0.05

    def __init__(self):
        super().__init__()
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = 0.0

    def norm_vel(self, vel=Speed.DEFAULT.value, minv=0.0, maxv=90.0):
        v_base = max(minv, min(maxv, float(vel))) / maxv
        v = minv + v_base * (maxv - minv)
        return v * self.SIM_SCALE

    def reset_speeds(self):
        self.v_x = 0.0
        self.v_y = 0.0
        self.v_turn = 0.0

    def go_from_angle(self, angle: float, vel=Speed.DEFAULT.value):
        """Move in an arbitrary direction; simulation decomposes angle into vx/vy components."""
        v = self.norm_vel(vel)
        rad = math.radians(angle)
        self.reset_speeds()
        self.v_x = v * math.cos(rad)
        self.v_y = v * math.sin(rad)

    def go_forward(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.reset_speeds()
        self.v_x = v

    def go_backward(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.reset_speeds()
        self.v_x = -v

    def spin_right(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.reset_speeds()
        self.v_turn = v / 40

    def spin_left(self, vel=Speed.DEFAULT.value):
        v = self.norm_vel(vel)
        self.reset_speeds()
        self.v_turn = - v / 40

    def stop(self):
        self.reset_speeds()
    